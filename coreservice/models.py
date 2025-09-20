import io
import random
import secrets
import string
import uuid
from datetime import datetime

import qrcode
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, _user_has_perm
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_countries.fields import CountryField


class AppSetting(models.Model):
    name = models.CharField(max_length=100, unique=True)
    settings = models.JSONField(default=dict)

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value
        self.save()

    def __str__(self):
        return f"Settings for {self.name}"
