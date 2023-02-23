from django.urls import path

from . import views

urlpatterns = [
    path("phoneVerify/<phone>/", views.phone_verification),
    path("emailVerify/<email>/", views.email_verification)
]