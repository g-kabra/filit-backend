"""Schemas for the Gold app"""
from datetime import datetime
from django.db import models
from shortuuid.django_fields import ShortUUIDField, ShortUUID

from login.models import CustomUser
from payments.models import TransactionDetails

base_time = datetime.strptime(
    "2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")


class GoldRatesModel(models.Model):
    """
    Stores the current rates fetched from the API
    """
    block_id = models.CharField(max_length=10, null=True)
    expiry = models.DateTimeField(default=base_time)
    gold_buy = models.FloatField(default=0)
    gold_sell = models.FloatField(default=0)
    silver_buy = models.FloatField(default=0)
    silver_sell = models.FloatField(default=0)
    gold_buy_gst = models.FloatField(default=0)
    silver_buy_gst = models.FloatField(default=0)

    objects = models.Manager()


class GoldTokenModel(models.Model):
    """
    Stores the token for the API
    """
    initiate = models.DateTimeField(default=base_time)
    token = models.CharField(max_length=1500, null=True)
    token_type = models.CharField(max_length=20, null=True)

    objects = models.Manager()


class GoldInvestorModel(models.Model):
    """
    Stores the details of the investor
    """
    user_id = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gold_user_id = ShortUUIDField(
        length=15,
        prefix="goldfi_",
        primary_key=True,
        default=ShortUUID.uuid
    )

    # Nominee Details
    nominee_name = models.CharField(max_length=100, null=True)
    nominee_date_of_birth = models.DateField(null=True)
    nominee_relation = models.CharField(max_length=50)

    objects = models.Manager()


class GoldAddressModel(models.Model):
    """
    Stores the address(es) of the investor
    """
    gold_user_id = models.ForeignKey(
        GoldInvestorModel, on_delete=models.CASCADE)
    address_id = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    pincode = models.CharField(max_length=8)
    mobile = models.CharField(max_length=15)

    objects = models.Manager()


class GoldBankModel(models.Model):
    """
    Stores the bank(s) of the investor
    """
    gold_user_id = models.ForeignKey(
        GoldInvestorModel, on_delete=models.CASCADE)
    bank_id = models.CharField(max_length=10, null=True, unique=True)
    account_number = models.CharField(max_length=18)
    account_name = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=11)

    objects = models.Manager()


class GoldTransactionModel(models.Model):
    """
    Stores all transaction details
    """
    STATES = [
        (1, "CREATED"),
        (2, "LOCKED"),
        (3, "COMPLETED"),
    ]

    gold_user_id = models.ForeignKey(
        GoldInvestorModel, on_delete=models.CASCADE)
    gold_txn_id = ShortUUIDField(
        length=20,
        primary_key=True,
        default=ShortUUID.uuid
    )
    txn_id = models.CharField(max_length=100, null=True)
    payment_id = models.ForeignKey(
        TransactionDetails, on_delete=models.CASCADE, null=True)
    txn_type = models.CharField(max_length=4)
    block_id = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    lock_price = models.FloatField()
    metal_type = models.CharField(max_length=6)
    amount = models.FloatField(default=0)
    quantity = models.FloatField(default=0)

    status = models.CharField(max_length=10, choices=STATES, default=1)
    is_autopay = models.BooleanField(default=False)
    bank_id = models.ForeignKey(
        GoldBankModel, to_field="bank_id", null=True, on_delete=models.SET_NULL)

    objects = models.Manager()


class GoldHoldingsModel(models.Model):
    """
    Holds portfolio information
    """
    gold_user = models.ForeignKey(GoldInvestorModel, on_delete=models.CASCADE)
    gold_held = models.FloatField(default=0)
    gold_locked = models.FloatField(default=0)

    last_processed = models.DateTimeField(default=datetime.now)
    objects = models.Manager()
