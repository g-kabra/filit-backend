"""
Urls for the payments app
"""
from django.urls import path

from . import views

urlpatterns = [
    path("pay/", views.create_transaction),
    path("start-subscription/", views.start_subscription),
    path("check-payment/", views.check_payment),
    path("get-payments/", views.get_payments),
    path("authorize-subscription/", views.authorize_subscription),
    path("verify/", views.verify_transaction),
    path("verify-subscription/", views.verify_subscription),
    path("cancel-subscription/", views.cancel_subscription),
    path("check-subscription/", views.check_subscription),
    path("callback-debit/", views.verify_auto_debit),
    path("orders/", views.get_order_history),
]
