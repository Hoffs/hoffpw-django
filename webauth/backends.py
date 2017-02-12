from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
        This is a ModelBackend that allows authentication with either a username or an email.
    """

    def authenticate(self, username=None, password=None, **kwargs):
        user = self._authenticate_username(username=username, password=password)
        if user:
            return user
        user = self._authenticate_email(email=username, password=password)
        if user:
            return user
        else:
            return None

    def _authenticate_username(self, username=None, password=None):
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def _authenticate_email(self, email=None, password=None):
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
