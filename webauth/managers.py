import hashlib

from django.contrib.auth.models import BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not email or not username or not password:
            raise ValueError("User must have username, email and password")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomTokenManager(models.Manager):
    def get_or_create_or_update(self, **kwargs):
        user = kwargs.pop('user')
        try:
            token = self.get(user=user)
        except self.model.DoesNotExist:
            token = self.create(user=user)
        is_valid, key = self.validate_key(token=token)
        if not is_valid:
            token.key = key
            token.save(using=self._db)
        else:
            token.save(using=self._db)
        return token

    @staticmethod
    def validate_key(token):
        valid_key = hashlib.sha256()
        valid_key.update(token.user.password.encode('utf-8'))
        valid_key.update(str(token.user.last_login.timestamp()).encode('utf-8'))
        return valid_key.hexdigest() == token.key, valid_key.hexdigest()
