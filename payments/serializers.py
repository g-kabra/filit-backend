"""
Serializers of the payments app
"""

from rest_framework import serializers

from .models import AutopayModel, TransactionDetails


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializes the Transaction model
    """
    class Meta:
        """
        Meta class for the TransactionSerializer
        """
        model = TransactionDetails
        fields = '__all__'

class AutopaySerializer(serializers.ModelSerializer):
    """
    Serializes the Autopay model
    """
    class Meta:
        """
        Meta class for the AutopaySerializer
        """
        model = AutopayModel
        fields = '__all__'
