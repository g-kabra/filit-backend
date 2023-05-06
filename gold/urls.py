from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register_user),
    path("rates/", views.get_rates_view),
    path("register-bank/", views.register_bank),
    path("register-address/", views.register_address),
    path("buy/", views.buy)
]