from django.db import models

# Create your models here.

class InvestorModel(models.Model):
    lbUserId = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    title = models.CharField(max_length=3)
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
    mobile = models.CharField(max_length=15)
    dob = models.CharField(max_length=20)
    pan = models.CharField(max_length=15)
    # *-*-*-* bank details *-*-*-*-* #
    holderName = models.CharField(max_length=40)
    bankName = models.CharField(max_length=50)
    accountNumber = models.CharField(max_length=15)
    accountType = models.CharField(max_length=10)
    ifsc = models.CharField(max_length=30)
    # *-*-*-* bank details *-*-*-*-* #
    street1 = models.CharField(max_length=100)
    street2 = models.CharField(max_length=100)
    city = models.CharField(max_length=30)
    pin = models.IntegerField()
    ip = models.CharField(max_length=20)
    ua = models.CharField(max_length=20)
    timestamp = models.CharField(max_length=20)

class InvestmentModel(models.Model):
    lbUserID = models.CharField(max_length=10)
    txID = models.CharField(max_length=50)
    txType = models.CharField(max_length=6)
    amount = models.IntegerField()
    investmentType = models.CharField(max_length=15)
    txTime = models.CharField(max_length=10)

