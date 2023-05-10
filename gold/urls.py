from django.urls import path
from rest_framework import routers

from . import views

urlpatterns = [
    path("register/", views.register_user),
    path("getuser/", views.get_user),
    path("rates/", views.get_rates_view),
    path("register-bank/", views.register_bank),
    path("get-bank/", views.get_banks),
    path("delete-bank/", views.delete_bank),
    path("register-address/", views.register_address),
    path("setnominee/", views.set_nominee),
    path("buy/", views.buy),
    path("sell/", views.sell),
    path("start-autopay/", views.start_autopay),
]

router = routers.SimpleRouter()
router.register(r"transactions", views.TransactionViewSet, 'txn-details')
urlpatterns += router.urls