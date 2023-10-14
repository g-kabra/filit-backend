from django.urls import path

from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("phone-verify/<phone>/", views.phone_verification),
    path("email-verify/<email>/", views.email_verification),
    path("update-user/", views.add_data),
    path("daily-savings/", views.DailySavingsViews.as_view()),
    path("fillup/", views.FillUpViews.as_view()),
    path("total-savings/", views.get_total_savings),
    path("update-fillup/", views.update_fillups)
]

router = routers.SimpleRouter()
router.register(r"userapi", views.UserViewSet, 'user-details')
urlpatterns += router.urls

urlpatterns += [
    path('api-token-auth/', obtain_auth_token)
]
