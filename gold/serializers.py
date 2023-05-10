from .models import GoldTransactionModel

from rest_framework import serializers


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldTransactionModel
        fields = '__all__'