"""
Models for the payment integration
"""

from django.db import models
from shortuuid.django_fields import ShortUUIDField, ShortUUID

from login.models import CustomUser

# Create your models here.


class TransactionDetails(models.Model):
    """
    Stores the details of the payment transaction
    """
    INTENTS = [
        (1, "GOLD"),
    ]
    TYPES = [
        (1, "MANUAL"),
        (2, "AUTOPAY")
    ]
    txn_id = ShortUUIDField(
        length=15,
        prefix="pefi_",
        primary_key=True,
        default=ShortUUID.uuid
    )
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.BigIntegerField(default=0)
    completion_status = models.BooleanField(default=False)
    intent = models.CharField(max_length=1, choices=INTENTS, default="GOLD")
    txn_type = models.CharField(max_length=1, choices=TYPES, default="MANUAL")

    payment_instrument = models.CharField(max_length=20, null=True)
    payment_id = models.CharField(max_length=50, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = models.Manager()


class AutopayModel(models.Model):
    """
    Holds information regarding autopay mandate (subscription)
    """
    STATES = [
        (1, "CREATED"),
        (2, "ACTIVE"),
        (3, "SUSPENDED"),
        (4, "REVOKED"),
        (5, "CANCELLED"),
        (6, "PAUSED"),
        (7, "EXPIRED"),
        (8, "FAILED"),
        (9, "CANCEL_IN_PROGRESS")
    ]

    subscription_id = ShortUUIDField(
        length=15,
        prefix="pefisub_",
        primary_key=True,
        default=ShortUUID.uuid
    )
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.FloatField()  # In paise
    startdate = models.DateField()
    count = models.BigIntegerField()
    status = models.CharField(max_length=1, choices=STATES, default="CREATED")
    valid_till = models.DateTimeField(default=None, null=True)
    phonepe_subscription_id = models.CharField(max_length=100, null=True)

    objects = models.Manager()

class AuthRequest(models.Model):
    """""
    Stores the details of the authentication request
    """""
    auth_id = ShortUUIDField(
        length=15,
        prefix="pefi_",
        primary_key=True,
        default=ShortUUID.uuid
    )
    subscription = models.OneToOneField(AutopayModel, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    objects = models.Manager()

