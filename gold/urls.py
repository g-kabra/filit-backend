from django.urls import path
from rest_framework import routers

from . import views

urlpatterns = [
    path("user/", views.UserViews.as_view()),
    path("bank/", views.BankViews.as_view()),
    path("address/", views.AddressViews.as_view()),
    path("set-nominee/", views.set_nominee),
    path("buy/", views.buy),
    path("sell/", views.sell),
    path("rates/", views.get_rates_view),
    path("get-passbook/", views.get_passbook),
    path("get-invoice/", views.get_invoice),
    path("transactions-paginated/", views.get_paginated_transactions)
]

router = routers.SimpleRouter()
router.register(r"transactions", views.TransactionViewSet, 'txn-details')
urlpatterns += router.urls
