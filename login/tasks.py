"""
    Contains the scheduled tasks for the daily savings app.
"""

from __future__ import absolute_import, unicode_literals
from celery import shared_task

from login.models import UserDailySavings, UserTotalSavings
from payments.functions import make_debit_request

@shared_task(name='add_daily_savings')
def add_daily_savings():
    """
        Adds the daily savings for all users.
    """
    for savings in UserDailySavings.objects.filter(is_active=True):
        total_savings = UserTotalSavings.objects.get(user=savings.user)
        total_savings.daily_savings += savings.daily_savings_amount
        total_savings.savings += savings.daily_savings_amount
        total_savings.todays_savings += savings.daily_savings_amount
        total_savings.monthly_savings += savings.daily_savings_amount
        total_savings.current_savings += savings.daily_savings_amount
        if(total_savings.current_savings >= 100):
            amount = total_savings.current_savings
            total_savings.current_savings = 0
            make_debit_request(user=savings.user, amount=amount*100)
        total_savings.save()
        savings.processed += 1
        savings.save()