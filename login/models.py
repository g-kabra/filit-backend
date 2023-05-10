from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from shortuuid.django_fields import ShortUUIDField, ShortUUID

from .managers import CustomUserManager
# Create your models here.


class phoneModel(models.Model):
    mobile = models.IntegerField(blank=False)
    counter = models.IntegerField(default=0, blank=False)

    def __str__(self):
        return str(self.mobile)


class emailModel(models.Model):
    email = models.EmailField(blank=False)
    counter = models.IntegerField(default=0, blank=False)

    def __str__(self):
        return str(self.email)


class customUser(AbstractBaseUser, PermissionsMixin):
    user_id = ShortUUIDField(
        length=20,
        prefix="fi_",
        primary_key=True,
        default=ShortUUID.uuid
    )
    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(null=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=10, null=True)
    pan_number = models.CharField(max_length=20, null=True)
    authentication_stage = models.CharField(
        max_length=20, default='phone-verified')
    pincode = models.CharField(max_length=8, null=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()


    USERNAME_FIELD = 'mobile'

    def __str__(self):
        return self.first_name + " " + self.last_name
