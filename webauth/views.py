# Create your views here.
from django.http import Http404
from rest_framework import mixins
from rest_framework import parsers
from rest_framework import renderers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import update_session_auth_hash
from rest_framework.views import APIView

from webauth.serializers import UserSerializer, UserRegisterSerializer, UserPasswordChangeSerializer, \
    AuthTokenSerializer, DeauthTokenSerializer
from webauth.models import User, AuthToken
from webauth.permissions import IsOwnerOrReadOnly
from uuid import UUID


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                  mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (AllowAny, IsOwnerOrReadOnly)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.user.is_staff:
                queryset = self.filter_queryset(self.get_queryset())
                page = self.paginate_queryset(queryset=queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
            else:
                user = User.objects.filter(uuid=request.user.uuid).first()
                serializer = self.get_serializer(instance=user)
            return Response(serializer.data)
        else:
            return Response({"detail": "Not logged in."}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(self.request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        self.check_object_permissions(request=request, obj=instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request=request, *args, **kwargs)

    def create(self, request, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.create_user(self.request.data['username'], self.request.data['email'],
                                            self.request.data['password'])
            serializer.data['uuid'] = user.uuid
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'], serializer_class=UserPasswordChangeSerializer,
                  permission_classes=[IsAuthenticated, IsOwnerOrReadOnly], url_path='change_password')
    def set_password(self, request, pk=None):
        user = self.get_object()
        self.check_object_permissions(request=request, obj=user)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if request.user.is_superuser:
                new_password = request.data['old_password']
                user.set_password(new_password)
                user.save()
                return Response({"detail": "New password has been saved"}, status=status.HTTP_200_OK)
            else:
                old_password = request.data['old_password']
                new_password1 = request.data['new_password1']
                new_password2 = request.data['new_password2']
                if new_password1 == new_password2:
                    if user.check_password(old_password):
                        user.set_password(new_password2)
                        user.save()
                        return Response({"detail": "New password has been saved."}, status=status.HTTP_200_OK)
                    else:
                        return Response({"detail": "Old password doesn't match"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        try:
            uuid = UUID(self.kwargs['pk'], version=4)
            try:
                return User.objects.get(uuid=uuid)
            except User.DoesNotExist:
                raise Http404
        except ValueError:
            username = self.kwargs['pk']
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                raise Http404


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = (AllowAny,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.save()
        token = AuthToken.objects.get_or_create_or_update(user=user)
        return Response({'token': token.key})


class InvalidateToken(APIView):
    throttle_classes = ()
    permission_classes = (IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request, *args, **kwargs):
        token = request.auth
        token.invalidate_key()
        return Response({"detail": "Successfully logged out."})
