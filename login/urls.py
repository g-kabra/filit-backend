from django.urls import path

from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("phoneVerify/<phone>/", views.phone_verification),
    path("emailVerify/<email>/", views.email_verification),
    path("pincode/<pincode>/", views.pincode_add),
    path("updateuser/", views.add_data)
]

router = routers.SimpleRouter()
router.register(r"userapi", views.UserViewSet, 'user-details')
urlpatterns += router.urls

urlpatterns += [
    path('api-token-auth/', obtain_auth_token)
]