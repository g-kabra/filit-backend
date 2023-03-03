from django.urls import path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("phoneVerify/<phone>/", views.phone_verification),
    path("emailVerify/<email>/", views.email_verification),
]

router = routers.SimpleRouter()
router.register(r"userapi", views.UserViewSet)
urlpatterns += router.urls

urlpatterns += [path("gettoken/", obtain_auth_token)]
