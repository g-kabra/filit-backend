from django.db import models
from login.models import customUser
from datetime import datetime
from shortuuid.django_fields import ShortUUIDField, ShortUUID
import pytz

# Create your models here.

base_time = datetime.strptime(
    "2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
timezone = pytz.timezone('Asia/Kolkata')
base_time = timezone.localize(base_time)

class GoldRatesModel(models.Model):
    block_id = models.CharField(max_length=10, null=True)
    expiry = models.DateTimeField(default=base_time)
    gold_buy = models.FloatField(default=0)
    gold_sell = models.FloatField(default=0)
    silver_buy = models.FloatField(default=0)
    silver_sell = models.FloatField(default=0)
    gold_buy_gst = models.FloatField(default=0)
    silver_buy_gst = models.FloatField(default=0)


class GoldTokenModel(models.Model):
    expiry = models.DateTimeField(default=base_time)
    token = models.CharField(max_length=100, null=True)
    token_type = models.CharField(max_length=20, null=True)


class GoldInvestorModel(models.Model):
    user_id = models.OneToOneField(customUser, on_delete=models.CASCADE)
    gold_user_id = ShortUUIDField(
        length=15,
        prefix="goldfi_",
        primary_key=True,
        default=ShortUUID.uuid
    )

    # Nominee Details
    nomineeName = models.CharField(max_length=100, null=True)
    nomineeDateOfBirth = models.DateField(null=True)
    nomineeRelation = models.CharField(max_length=50)


class GoldAddressModel(models.Model):
    gold_user_id = models.ForeignKey(
        GoldInvestorModel, on_delete=models.CASCADE)
    address_id = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    pincode = models.CharField(max_length=8)
    mobile = models.CharField(max_length=15)


class GoldBankModel(models.Model):
    gold_user_id = models.ForeignKey(
        GoldInvestorModel, on_delete=models.CASCADE)
    bank_id = models.CharField(max_length=10, null=True, unique=True)
    account_number = models.CharField(max_length=18)
    account_name = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=11)


class GoldTransactionModel(models.Model):
    gold_user_id = models.ForeignKey(
        GoldInvestorModel, on_delete=models.CASCADE)
    gold_txn_id = ShortUUIDField(
        length=20,
        primary_key=True,
        default=ShortUUID.uuid
    )
    txn_type = models.CharField(max_length=4)
    block_id = models.CharField(max_length=10)
    lock_price = models.FloatField()
    metal_type = models.CharField(max_length=6)
    amount = models.FloatField()
    # * Change to choice based
    status = models.BooleanField(default=False)
    is_autopay = models.BooleanField(default=False)
    bank_id = models.ForeignKey(
        GoldBankModel, to_field="bank_id", null=True, on_delete=models.SET_NULL)


class GoldAutopayModel(models.Model):
    gold_user = models.ForeignKey(GoldInvestorModel, on_delete=models.CASCADE)
    autopay_amount = models.IntegerField()
    startdate = models.DateField()
    processed = models.IntegerField(default=0)
