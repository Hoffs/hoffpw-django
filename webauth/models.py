import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.db import models


# Create your models here.
from webauth.managers import CustomUserManager


class User(AbstractBaseUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=32, unique=True)
    email = models.EmailField(max_length=254, unique=True)
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
