# Create your views here.
from django.http import Http404
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from webauth.serializers import UserSerializer, UserRegisterSerializer, UserPasswordChangeSerializer, \
    AuthTokenSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, EmailConfirmSerializer
from webauth.models import User, AuthToken, PasswordResetToken, EmailToken
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
    def set_password(self, request):
        user = self.get_object()
        self.check_object_permissions(request=request, obj=user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.is_superuser:
            new_password = serializer.data['old_password']
            user.set_password(new_password)
            user.save()
            return Response({"detail": "New password has been saved"}, status=status.HTTP_200_OK)
        else:
            old_password = serializer.data['old_password']
            new_password = serializer.data['new_password']
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return Response({"detail": "New password has been saved."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Old password doesn't match"}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.is_valid()
        if serializer.validated_data.get('email') and serializer.context['request'].user.email \
                != serializer.validated_data.get('email'):
            serializer.validated_data['email_verified'] = False
        serializer.save()

    def get_object(self):
        identifier = self.kwargs['pk']
        obj = User.objects.get_from_uuid_or_username(identifier=identifier)
        if obj:
            self.check_object_permissions(request=self.request, obj=obj)
            return obj
        else:
            raise Http404

    def get_queryset(self):
        if not self.request.user.is_anonymous and self.request.user.is_admin():
            return User.objects.all()
        elif not self.request.user.is_anonymous:
            return User.objects.filter(uuid=self.request.user.uuid)
        else:
            return User.objects.none()


class PasswordReset(APIView):
    """
        API endpoint for sending a request for resetting the password.
    """
    throttle_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.data['email'])
            token = PasswordResetToken.objects.make_token(user=user)
            if token:
                """TODO: Send an email to user."""
                return Response({"details": token.key}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"details": "No user with such email found."}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirm(APIView):
    """
        API endpoint for resetting the password with given token.
    """
    throttle_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = PasswordResetToken.objects.validate_key(key=serializer.data['token'])
        if token:
            token.user.set_password(serializer.data['password'])
            token.user.save()
            return Response({"details": "Password has been successfully reset."}, status=status.HTTP_200_OK)
        else:
            return Response({"details": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


class UserEmailConfirmRequest(APIView):
    """
        API endpoint for sending a request for confirming the email.
    """
    throttle_classes = ()
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        if user.email_verified:
            return Response({"detail": "Email already verified."})
        else:
            token = EmailToken.objects.make_token(user=user)
            return Response({"detail": token.key})


class UserEmailConfirm(APIView):
    """
        API endpoint for confirming email with given token.
    """
    throttle_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = EmailConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = EmailToken.objects.validate_key(key=serializer.data['token'])
        if token:
            token.user.email_verified = True
            token.user.save()
            return Response({"detail": "Email has been successfully verified."}, status=status.HTTP_200_OK)
        else:
            return Response({"details": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


class ObtainToken(APIView):
    """
        API endpoint for obtaining authentication token with given details.
    """
    throttle_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.save()
        token = AuthToken.objects.get_or_create_or_update(user=user)
        return Response({'token': token.key})


class InvalidateToken(APIView):
    """
        API endpoint for invalidating the authentication token.
    """
    throttle_classes = ()
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        token = request.auth
        token.invalidate_key()
        return Response({"detail": "Successfully logged out."})
