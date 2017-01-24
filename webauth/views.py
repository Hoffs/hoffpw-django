# Create your views here.0
from django.http import Http404
from rest_framework import mixins
from rest_framework import parsers
from rest_framework import renderers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from webauth.serializers import UserSerializer, UserRegisterSerializer, UserPasswordChangeSerializer, \
    AuthTokenSerializer
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

    def create(self, request, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            User.objects.create_user(self.request.data['username'], self.request.data['email'],
                                     self.request.data['password'])
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
                obj = User.objects.get(uuid=uuid)
                self.check_object_permissions(request=self.request, obj=obj)
                return obj
            except User.DoesNotExist:
                raise Http404
        except ValueError:
            username = self.kwargs['pk']
            try:
                obj = User.objects.get(username=username)
                self.check_object_permissions(request=self.request, obj=obj)
                return obj
            except User.DoesNotExist:
                raise Http404

    def get_queryset(self):
        if not self.request.user.is_anonymous and self.request.user.is_admin():
            return User.objects.all()
        elif not self.request.user.is_anonymous:
            return User.objects.filter(uuid=self.request.user.uuid)
        else:
            return User.objects.none()


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
    permission_classes = (IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request, *args, **kwargs):
        token = request.auth
        token.invalidate_key()
        return Response({"detail": "Successfully logged out."})
