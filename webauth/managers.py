import hashlib
import uuid

from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.db import models

from webauth import settings


class CustomUserManager(BaseUserManager):
    def get_from_uuid_or_username(self, identifier):
        response = self.get_from_uuid(identifier)
        if response:
            return response

        response = self.get_from_username(identifier)
        if response:
            return response
        else:
            return None

    def get_from_uuid(self, identifier):
        try:
            from uuid import UUID
            user_id = UUID(identifier, version=4)
            try:
                obj = self.model.objects.get(uuid=user_id)
                return obj
            except self.model.DoesNotExist:
                return None
        except ValueError:
            return None

    def get_from_username(self, identifier):
        try:
            obj = self.model.objects.get(username=identifier)
            return obj
        except self.model.DoesNotExist:
            return None

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


class ConfirmManager(models.Manager):
    def create(self, user):
        if not user:
            raise ValueError("User must have username, email and password")
        verification_token = uuid.uuid4().hex
        token = self.model(
            user=user,
            key=verification_token,
            active=True,
        )
        token.save(using=self._db)
        return token

    def update_token(self, token):
        verification_token = uuid.uuid4().hex
        token.key = verification_token
        token.active = True
        token.count += 1
        token.save(using=self._db)
        return token

    def make_token(self, **kwargs):
        user = kwargs.pop('user')
        try:
            token = self.get(user=user)
            self.update_token(token)
        except self.model.DoesNotExist:
            token = self.create(user=user)
        return token

    def validate_key(self, key):
        try:
            token = self.get(key=key)
            current_time = timezone.now()
            expiration_time = settings.VERIFICATION_KEY_EXPIRATION_HOURS * 3600
            if abs(token.updated - current_time).total_seconds() < expiration_time and token.active:
                self.disable_key(key=key)
                return token
            else:
                return None
        except self.model.DoesNotExist:
            return None

    def disable_key(self, key):
        try:
            token = self.get(key=key)
            token.active = False
            token.save()
        except self.model.DoesNotExist:
            pass
