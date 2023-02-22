from django.urls import path

from . import views

urlpatterns = [
    path("<phone>/", views.phone_verification)
]