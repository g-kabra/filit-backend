from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import viewsets

from datetime import datetime
from random import randint
import base64
import pyotp

from .models import phoneModel, emailModel
from .serializers import CustomUserSerializer

# Create your views here.


class generateKey:
    @staticmethod
    def returnValue(base):
        return str(base) + str(datetime.date(datetime.now())) + "secure"


@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([])
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
        # API CALL SMS API
        return Response({"otp": OTP.at(mobile.counter)}, status=200)
    elif request.method == "POST":
        try:
            mobile = phoneModel.objects.get(mobile=phone)
        except ObjectDoesNotExist:
            return Response("Doesn't Exist", status=404)
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())
        OTP = pyotp.HOTP(key)
        if OTP.verify(request.data.get("otp"), mobile.counter):
            User = get_user_model()
            if User.objects.all().filter(mobile=phone):
                user = User.objects.get(mobile=phone)
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key, 'authentication_stage': user.authentication_stage}, status=200)
            else:
                # If first time, create user and return new user token
                user = User.objects.create(mobile=phone)
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key, 'authentication_stage': user.authentication_stage}, status=200)
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
            # pass
            # Update User
            user = request.user
            user.authentication_stage = 'email-verified'
            user.email = email.email
            user.save()
            return Response("Verified", status=200)
        return Response("Wrong OTP", status=400)


@api_view(["POST"])
def add_data(request, *args, **kwargs):
    user = request.user
    details = request.data
    serialized = CustomUserSerializer(user, details, partial=True)
    if serialized.is_valid():
        user.authentication_stage = 'profile-verified'
        serialized.save()
        return Response(serialized.data)
    return Response(serialized.errors, status=400)


class UserViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (AllowAny, )
    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_admin:
                return self.queryset
            return self.queryset.filter(mobile=self.request.user.mobile)
        return None
