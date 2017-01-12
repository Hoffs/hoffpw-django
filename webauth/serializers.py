from webauth.models import User
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
    new_password1 = serializers.CharField(required=True, max_length=254)
    new_password2 = serializers.CharField(required=True, max_length=254)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

