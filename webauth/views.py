# Create your views here.
from django.http import Http404
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import update_session_auth_hash

from webauth.serializers import UserSerializer, UserRegisterSerializer, UserPasswordChangeSerializer
from webauth.models import User
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
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.create_user(self.request.data['username'], self.request.data['email'],
                                            self.request.data['password'])
            serializer.data['uuid'] = user.uuid
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['patch'], serializer_class=UserPasswordChangeSerializer,
                  permission_classes=[IsAuthenticated, IsOwnerOrReadOnly], url_path='change_password')
    def set_password(self, request, pk=None):
        self.check_object_permissions(request=request, obj=User.objects.filter(uuid=pk).first())
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if request.user.is_superuser:
                user = User.objects.filter(uuid=pk).first()
                new_password = request.data['old_password']
                user.set_password(new_password)
                user.save()
                return Response({"detail": "New password has been saved"}, status=status.HTTP_200_OK)
            else:
                user = request.user
                if str(user.uuid) == pk:
                    old_password = request.data['old_password']
                    new_password1 = request.data['new_password1']
                    new_password2 = request.data['new_password2']
                    if new_password1 == new_password2:
                        if user.check_password(old_password):
                            user.set_password(new_password2)
                            user.save()
                            update_session_auth_hash(request, user)
                            return Response({"detail": "New password has been saved."}, status=status.HTTP_200_OK)
                        else:
                            return Response({"detail": "Old password doesn't match"},
                                            status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"detail": "Can't change another users password."})

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
