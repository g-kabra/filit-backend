from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
import base64, pyotp
from datetime import datetime

from .models import phoneModel

# Create your views here.

class generateKey:
    @staticmethod
    def returnValue(phone):
        return str(phone) + str(datetime.date(datetime.now())) + "secure"
    
@api_view(['GET', 'POST'])
def phone_verification(request, phone, *args, **kwargs):
    # phone = request.data.get('phone')
    if(request.method == 'GET'):
        try:
            mobile = phoneModel.objects.get(mobile = phone)
        except ObjectDoesNotExist:
            phoneModel.objects.create(mobile = phone)
            mobile = phoneModel.objects.get(mobile = phone)
        mobile.counter += 1
        mobile.save()
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())
        OTP = pyotp.HOTP(key)
        return Response({"OTP": OTP.at(mobile.counter)}, status=200)
    if(request.method == 'POST'):
        try:
            mobile = phoneModel.objects.get(mobile = phone)
        except ObjectDoesNotExist:
            return Response("Doesn't Exist", status=404)
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())
        OTP = pyotp.HOTP(key)
        print(request.POST)
        if OTP.verify(request.data.get('otp'), mobile.counter):
            return Response("Verified", status=200)
        return Response("Wrong OTP", status=400)