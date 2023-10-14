from .models import GoldTransactionModel, GoldBankModel

from rest_framework import serializers


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldTransactionModel
        fields = '__all__'

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldBankModel
        fields = '__all__'