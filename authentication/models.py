from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser
from rest_framework.authtoken.models import Token

from .managers import CustomUserManager


# Create your models here.

class phoneModel(models.Model):
    mobile = models.IntegerField(blank=False)
    counter = models.IntegerField(default = 0, blank=False)

    def __str__(self):
        return str(self.mobile)

class emailModel(models.Model):
    email = models.EmailField(blank=False)
    counter = models.IntegerField(default = 0, blank=False)

    def __str__(self):
        return str(self.email)
    
class customUser(AbstractBaseUser):
    pass
    email = models.EmailField(verbose_name='email address', unique=True)
    mobile = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    dob = models.DateField(default="2000-01-01")
    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.first_name + " " + self.last_name

