from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import viewsets

from datetime import datetime
from random import randint
import base64, pyotp

from .models import phoneModel, emailModel
from .serializers import CustomUserSerializer

# Create your views here.

class generateKey:
    @staticmethod
    def returnValue(base):
        return str(base) + str(datetime.date(datetime.now())) + "secure"


@api_view(["GET", "POST"])
def phone_verification(request, phone, *args, **kwargs):
    if request.method == "GET":
        try:
            mobile = phoneModel.objects.get(mobile=phone)
        except ObjectDoesNotExist:
            phoneModel.objects.create(mobile=phone)
            mobile = phoneModel.objects.get(mobile=phone)
        # ? Generating counter for OTP
        mobile.counter = randint(1, 10000)
        mobile.save()
        keygen = generateKey()
        # ? Random key generated
        key = base64.b32encode(keygen.returnValue(phone).encode())
        OTP = pyotp.HOTP(key)
        #API CALL SMS API
        return Response({"OTP": OTP.at(mobile.counter)}, status=200)
    if request.method == "POST":
        try:
            mobile = phoneModel.objects.get(mobile=phone)
        except ObjectDoesNotExist:
            return Response("Doesn't Exist", status=404)
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())
        OTP = pyotp.HOTP(key)
        if OTP.verify(request.data.get("otp"), mobile.counter):
            User = get_user_model()
            if User.objects.all().filter(mobile=mobile):
                user = User.objects.get(mobile=phone)
                token, created = Token.objects.get_or_create(user = user)
                return Response({'token':token.key}, status=200)
            else:
                # If first time, create user and return new user token
                user = User.objects.create(mobile=phone)
                token, created = Token.objects.get_or_create(user = user)
                return Response({'token':token.key}, status=200)
        return Response("Wrong OTP", status=400)


@api_view(["GET", "POST"])
def email_verification(request, email, *args, **kwargs):
    if request.method == "GET":
        try:
            email = emailModel.objects.get(email=email)
        except ObjectDoesNotExist:
            emailModel.objects.create(email=email)
            email = emailModel.objects.get(email=email)
        email.counter = randint(1, 10000)
        email.save()
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(email).encode())
        OTP = pyotp.HOTP(key)
        return Response({"OTP": OTP.at(email.counter)}, status=200)
    if request.method == "POST":
        try:
            email = emailModel.objects.get(email=email)
        except ObjectDoesNotExist:
            return Response("Doesn't exist", status=404)
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(email).encode())
        OTP = pyotp.HOTP(key)
        if OTP.verify(request.data.get("otp"), email.counter):
            pass
            #Update User
            User = get_user_model()
            user = request.user
            user.authentication_stage = 'email-verified'
            user.email = email.email
            user.save()
            return Response("Verified", status=200)
        return Response("Wrong OTP", status=400)
    
class UserViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (AllowAny, )
    def get_queryset(self):
        if self.request.user.is_admin:
            return self.queryset
        return self.queryset.filter(mobile=self.request.user.mobile)