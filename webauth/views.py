# Create your views here.
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.viewsets import GenericViewSet
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import update_session_auth_hash

from webauth.serializers import UserSerializer, UserRegisterSerializer, UserPasswordChangeSerializer
from webauth.models import User


class UserViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRegisterViewSet(viewsets.ViewSetMixin, generics.CreateAPIView):
    """
    API endpoint that allows users to be created.
    """
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        User.objects.create_user(self.request.data['username'], self.request.data['email'], self.request.data['password'])


class PasswordChangeViewSet(viewsets.ViewSetMixin, generics.UpdateAPIView):
    """
    API endpoint for changing user passwords.
    """
    serializer_class = UserPasswordChangeSerializer
    permission_classes = (AllowAny,)
    queryset = User.objects.all()

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = request.user
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
                    return Response({"detail": "Old password doesn't match"})
            else:
                return Response({"detail": "Passwords do not match."})



