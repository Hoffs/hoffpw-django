from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from webauth.models import User, AuthToken
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for getting information about users.
    """

    class Meta:
        model = User
        fields = ('uuid', 'username', 'email', 'is_staff', 'is_active', 'date_joined', 'last_login',)
        read_only_fields = ('is_staff', 'is_active')


class UserRegisterSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for registering new users.
    """

    class Meta:
        model = User
        fields = ('username', 'password', 'email',)


class UserPasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(required=True, max_length=254)
    new_password = serializers.CharField(required=True, max_length=254)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a reset token for password.
    """
    email = serializers.EmailField(max_length=254, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for resetting the password with given reset token.
    """
    token = serializers.CharField(max_length=254, required=True)
    password = serializers.CharField(max_length=254, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

class EmailConfirmRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a confirmation token for email.
    """
    class Meta:
        model = User
        fields = ('email',)

class EmailConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming email with given verification token.
    """
    token = serializers.CharField(max_length=254, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for logging in and receiving authentication token.
    """
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                # From Django 1.10 onwards the `authenticate` call simply
                # returns `None` for is_active=False users.
                # (Assuming the default `ModelBackend` authentication backend.)
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg, code='authorization')
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class DeauthTokenSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for invalidating given authentication token.
    """
    class Meta:
        model = AuthToken
        fields = ('key',)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
