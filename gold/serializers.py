from .models import GoldTransactionModel, GoldBankModel, GoldHoldingsModel

from rest_framework import serializers


class TransactionSerializer(serializers.ModelSerializer):
    completion_status = serializers.CharField(source='payment_id.completion_status')
    intent = serializers.CharField(source='payment_id.intent')
    txn_type = serializers.CharField(source='payment_id.txn_type')

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