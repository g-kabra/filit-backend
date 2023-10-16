"""
    Contains the scheduled tasks for the gold app.
"""

from __future__ import absolute_import, unicode_literals
from datetime import datetime, timedelta
from celery import shared_task

from .models import GoldHoldingsModel, GoldTransactionModel

@shared_task(name='update_locked_gold')
def update_locked_gold():
    """
    Updates the locked gold for all users.
    """
    for transaction in GoldTransactionModel.objects.filter(status="LOCKED", timestamp__lte=datetime.now() - timedelta(days=2)):
        gold_user = transaction.gold_user_id
        transaction.status = "COMPLETED"
        transaction.save()
        holding = GoldHoldingsModel.objects.get(gold_user=gold_user)
        holding.gold_locked -= transaction.amount
        holding.gold_held += transaction.amount
        holding.save()