from .models import GoldTransactionModel, GoldBankModel, GoldHoldingsModel

from rest_framework import serializers


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldTransactionModel
        fields = '__all__'

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldBankModel
        fields = '__all__'

class HoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldHoldingsModel
        fields = '__all__'