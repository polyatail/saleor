from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.translation import pgettext_lazy

from ..product.models import Category


class UserManager(BaseUserManager):
    def create_user(
            self, username, password=None, is_staff=False, is_active=True,
            **extra_fields):
        """Create a user instance with the given email and password."""
        user = self.model(
            username=username, is_active=is_active, is_staff=is_staff,
            **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        return self.create_user(
            username, password, is_staff=True, **extra_fields)


class User(AbstractBaseUser):
    username = models.CharField(
        pgettext_lazy('User field', 'username'), unique=True, max_length=64)
    is_staff = models.BooleanField(
        pgettext_lazy('User field', 'staff status'),
        default=False)
    is_active = models.BooleanField(
        pgettext_lazy('User field', 'active'),
        default=True)
    company = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    date_joined = models.DateTimeField(
        pgettext_lazy('User field', 'date joined'),
        default=timezone.now, editable=False)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
