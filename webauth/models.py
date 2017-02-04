import uuid
import hashlib

from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from hoffpw import settings
from webauth.managers import CustomUserManager, CustomTokenManager, ConfirmManager


class User(AbstractBaseUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=32, unique=True, validators=[MinLengthValidator(4), ])
    email = models.EmailField(max_length=254, unique=True)
    email_verified = models.BooleanField(default=False)
    password = models.CharField(max_length=254)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']

    objects = CustomUserManager()

    def get_full_name(self):
        return self.uuid

    def get_short_name(self):
        return self.username

    def is_admin(self):
        return self.is_staff or self.is_superuser

    class Meta:
        ordering = ('date_joined',)

class PasswordResetToken(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='reset_token',
        on_delete=models.CASCADE, verbose_name=_("User"),
        primary_key=True
    )
    key = models.CharField(_("Key"), max_length=254)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    updated = models.DateTimeField(_("Updated"), auto_now=True)
    count = models.IntegerField(default=0)
    active = models.BooleanField(default=False)

    objects = ConfirmManager()

class EmailToken(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='confirm_token',
        on_delete=models.CASCADE, verbose_name=_("User"),
        primary_key=True
    )
    key = models.CharField(_("Key"), max_length=254)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    updated = models.DateTimeField(_("Updated"), auto_now=True)
    count = models.IntegerField(default=0)
    active = models.BooleanField(default=False)

    objects = ConfirmManager()

class AuthToken(models.Model):
    key = models.CharField(_("Key"), max_length=60)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name=_("User"),
        primary_key=True
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    updated = models.DateTimeField(_("Updated"), auto_now=True)

    objects = CustomTokenManager()

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def is_valid(self):
        valid_key = hashlib.sha256()
        valid_key.update(self.user.password.encode('utf-8'))
        valid_key.update(str(self.user.last_login.timestamp()).encode('utf-8'))
        return valid_key.hexdigest() == self.key

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(AuthToken, self).save(*args, **kwargs)

    def generate_key(self):
        key = hashlib.sha256()
        key.update(self.user.password.encode('utf-8'))
        key.update(str(self.user.last_login.timestamp()).encode('utf-8'))
        return key.hexdigest()

    def invalidate_key(self):
        self.key = "logged_out"
        self.save()

    def __str__(self):
        return self.key
