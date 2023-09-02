from .models import GoldTransactionModel, GoldBankModel, GoldDailySavingsModel

from rest_framework import serializers


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldTransactionModel
        fields = '__all__'

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldBankModel
        fields = '__all__'

class DailySavingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldDailySavingsModel
        fields = '__all__'