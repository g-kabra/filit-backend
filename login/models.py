from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from shortuuid.django_fields import ShortUUIDField, ShortUUID

from .managers import CustomUserManager
# Create your models here.


class PhoneModel(models.Model):
    """
        Stores the user phone details
    """
    mobile = models.BigIntegerField(blank=False)
    counter = models.BigIntegerField(default=0, blank=False)

    objects = models.Manager()

    def __str__(self):
        return str(self.mobile)


class EmailModel(models.Model):
    """
        Stores the user email details
    """
    email = models.EmailField(blank=False)
    counter = models.BigIntegerField(default=0, blank=False)

    objects = models.Manager()

    def __str__(self):
        return str(self.email)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
        Stores the user details
    """
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
    address = models.CharField(max_length=100)
    authentication_stage = models.CharField(
        max_length=20, default='phone-verified')
    pincode = models.CharField(max_length=8, null=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile'

    def __str__(self):
        return self.first_name + " " + self.last_name


class FillUp(models.Model):
    """
        Stores the fillups being made
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fillup_value = models.BigIntegerField(default=0)
    base_value = models.BigIntegerField(default=0)
    intent = models.CharField(max_length=50, default="Unknown")

    is_daily_savings = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return str(self.user) + " " + str(self.fillup_value)


class UserTotalSavings(models.Model):
    """
        Stores the total savings being made
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    savings = models.BigIntegerField(default=0)

    daily_savings = models.BigIntegerField(default=0)
    fillups = models.BigIntegerField(default=0)

    fillup_multiplier = models.BigIntegerField(default=1)
    fillup_is_active = models.BooleanField(default=False)

    monthly_savings = models.BigIntegerField(default=0)
    todays_savings = models.BigIntegerField(default=0)
    todays_spendings = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return str(self.user) + " " + str(self.savings)

class UserDailySavings(models.Model):
    """
        Stores a user's daily savings details
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    daily_savings_amount = models.FloatField()
    startdate = models.DateField()
    is_active = models.BooleanField(default=True)
    processed = models.BigIntegerField(default=0)

    objects = models.Manager()

    def __str__(self):
        return str(self.user) + " " + str(self.daily_savings_amount)
