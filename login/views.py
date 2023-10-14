"""
Contains views for the login app
"""
from datetime import datetime
from random import randint
import base64
import pyotp

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework import views, viewsets


from .models import FillUp, PhoneModel, EmailModel, CustomUser, UserDailySavings, UserTotalSavings
from .serializers import CustomUserSerializer, DailySavingsSerializer, FillUpSerializer, UserTotalSavingsSerializer
from .functions import make_response

# Create your views here.


class generateKey:
    @staticmethod
    def returnValue(base):
        return str(base) + str(datetime.date(datetime.now())) + "secure"


@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([])
def phone_verification(request, phone, *args, **kwargs):
    """
        Used to verify the phone number of the user
    """
    if request.method == "GET":
        try:
            mobile = PhoneModel.objects.get(mobile=phone)
        except ObjectDoesNotExist:
            PhoneModel.objects.create(mobile=phone)
            mobile = PhoneModel.objects.get(mobile=phone)
        # ? Generating counter for OTP
        mobile.counter = randint(1, 10000)
        mobile.save()
        keygen = generateKey()
        # ? Random key generated
        key = base64.b32encode(keygen.returnValue(phone).encode())
        OTP = pyotp.HOTP(key)
        OTP = OTP.at(mobile.counter)
        # API CALL SMS API
        return Response(make_response("OTP Generated Successfully", data={
            "otp": OTP
        }))
    elif request.method == "POST":
        try:
            mobile = PhoneModel.objects.get(mobile=phone)
        except ObjectDoesNotExist:
            return Response(make_response("Phone not found", status=400, errors=[
                {
                    "code": "PHONE_NOT_FOUND",
                    "message": "Phone not found"
                }
            ]))
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())
        OTP = pyotp.HOTP(key)
        if OTP.verify(request.data.get("otp"), mobile.counter):
            User = get_user_model()
            if User.objects.all().filter(mobile=phone):
                user = User.objects.get(mobile=phone)
                token, created = Token.objects.get_or_create(user=user)
                return Response(make_response("OTP Verification Successful", data={
                    "token": token.key,
                    "authentication_stage": user.authentication_stage
                }))
            # If first time, create user and return new user token
            user = User.objects.create(mobile=phone)
            token, created = Token.objects.get_or_create(user=user)
            return Response(make_response("OTP Verification Successful", data={
                "token": token.key,
                "authentication_stage": user.authentication_stage
            }))
        return Response(make_response("OTP Verification failed", status=400, errors=[
            {
                "code": "OTP_INCORRECT",
                "message": "OTP is incorrect"
            }
        ]))


@api_view(["GET", "POST"])
def email_verification(request, email, *args, **kwargs):
    if request.method == "GET":
        try:
            email = EmailModel.objects.get(email=email)
        except ObjectDoesNotExist:
            EmailModel.objects.create(email=email)
            email = EmailModel.objects.get(email=email)
        email.counter = randint(1, 10000)
        email.save()
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(email).encode())
        OTP = pyotp.HOTP(key)
        OTP = OTP.at(email.counter)
        return Response(make_response("OTP Generated Successfully", data={
            "otp": OTP,
        }))
    if request.method == "POST":
        try:
            email = EmailModel.objects.get(email=email)
        except ObjectDoesNotExist:
            return Response(make_response("Email not found", status=400, errors=[
                {
                    "code": "EMAIL_NOT_FOUND",
                    "message": "Email not found"
                }
            ]))
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
            return Response(make_response("Verified successfully", data=CustomUserSerializer(user).data))
        return Response(make_response("OTP Verification failed", errors=[
            {
                "code": "OTP_INCORRECT",
                "message": "OTP is incorrect"
            }
        ], status=400))


@api_view(["POST"])
def add_data(request, *args, **kwargs):
    """
        Used to update the data of the user
    """
    user = request.user
    details = request.data
    serialized = CustomUserSerializer(user, details, partial=True)
    if serialized.is_valid():
        user.authentication_stage = 'profile-verified'
        serialized.save()
        return Response(serialized.data)
    return Response(serialized.errors, status=400)


class UserViewSet(viewsets.ModelViewSet):
    """
        Viewset to view details of the user
    """
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (AllowAny, )

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_admin:
                return self.queryset
            return self.queryset.filter(user=self.request.user)
        return None


class DailySavingsViews(views.APIView):
    """
    Daily savings related views
    """

    def post(self, request):
        """
        Start daily savings for a user
        """
        user = request.user

        startdate = datetime.utcnow().date()
        amount = request.data.get("daily_savings_amount")

        # ? Discontinue previous
        daily_savings = UserDailySavings.objects.filter(
            user=user).first()
        if daily_savings:
            daily_savings.is_active = False
            daily_savings.save()

        daily_savings = UserDailySavings.objects.create(
            user=user,
            daily_savings_amount=amount,
            startdate=startdate
        )
        return Response(make_response("Daily savings started successfully", data={
            "daily_savings_amount": daily_savings.daily_savings_amount,
            "start_date": daily_savings.startdate
        }))

    def get(self, request):
        """
        Get daily savings items
        """
        user = request.user
        daily_savings = UserDailySavings.objects.filter(
            user=user, is_active=True).first()
        if not daily_savings:
            return Response(make_response(
                "Daily savings not started",
                status=400,
                errors=[
                    {
                        "code": "DAILY_SAVINGS_NOT_STARTED",
                        "message": "Daily savings not started for user"
                    }
                ]
            ))
        return Response(make_response("Daily savings fetched successfully", data={
            "daily_savings_amount": daily_savings.daily_savings_amount,
            "start_date": daily_savings.startdate,
            "processed": daily_savings.processed,
            "is_active": daily_savings.is_active
        }))

    def put(self, request):
        """
        Update daily savings items
        """
        user = request.user
        daily_savings = UserDailySavings.objects.filter(
            user=user, is_active=True).first()
        if not daily_savings:
            return Response(make_response(
                "Daily savings not started",
                status=400,
                errors=[
                    {
                        "code": "DAILY_SAVINGS_NOT_STARTED",
                        "message": "Daily savings not started for user"
                    }
                ]
            ))
        serializer = DailySavingsSerializer(
            daily_savings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(make_response("Daily savings updated successfully", data=serializer.data))
        return Response(make_response("Couldn't update daily savings", data=serializer.errors, status=400, errors=[
            {
                "code": "DAILY_SAVINGS_UPDATE_FAILED",
                "message": "Couldn't update daily savings"
            }
        ]))

    def delete(self, request):
        """ 
            Delete daily savings item
        """
        user = request.user
        daily_savings = UserDailySavings.objects.filter(
            user=user).first()
        if not daily_savings:
            return Response(make_response(
                "Daily savings not started",
                status=400,
                errors=[
                    {
                        "code": "DAILY_SAVINGS_NOT_STARTED",
                        "message": "Daily savings not started for user"
                    }
                ]
            ))
        daily_savings.is_active = False
        daily_savings.save()
        return Response(make_response("Daily savings stopped successfully"))


class FillUpViews(views.APIView):
    """
        Fillup related views
    """

    def post(self, request):
        user = request.user
        fillup_value = request.data.get("fillup_value")
        base_value = request.data.get("base_value")
        intent = request.data.get("intent")

        user_savings, c = UserTotalSavings.objects.get_or_create(user=user)

        # ? Check if fillups are active
        if not user_savings.fillup_is_active:
            return Response(make_response("Fillups are not active", status=400, errors=[
                {
                    "code": "FILLUPS_NOT_ACTIVE",
                    "message": "Fillups are not active"
                }
            ]))

        fillup = FillUp.objects.create(
            user=user,
            fillup_value=fillup_value*user_savings.fillup_multiplier,
            base_value=base_value,
            intent=intent
        )

        # ? Update user savings
        user_savings.savings += fillup_value
        user_savings.fillups += fillup_value
        user_savings.todays_savings += fillup_value
        user_savings.monthly_savings += fillup_value
        user_savings.todays_spendings += base_value
        user_savings.save()

        return Response(make_response("Fillup created successfully", data=FillUpSerializer(fillup).data))

    def get(self, request):
        """
            Paginated view for fillups
        """
        user = request.user
        fillups = FillUp.objects.filter(user=user).order_by("-created_at")
        paginator = Paginator(fillups, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return Response(make_response("Fillups fetched successfully", data={'items': FillUpSerializer(page_obj.object_list, many=True).data, 'has_next': page_obj.has_next()}))


@api_view(["GET"])
def get_total_savings(request):
    """
        Get total savings data for a user
    """
    user = request.user
    total_savings = UserTotalSavings.objects.filter(user=user).first()
    if not total_savings:
        return Response(make_response("Total savings not found", status=400, errors=[
            {
                "code": "TOTAL_SAVINGS_NOT_FOUND",
                "message": "Total savings not found"
            }
        ]))
    return Response(make_response("Total savings fetched successfully", data=UserTotalSavingsSerializer(total_savings).data))


@api_view(["POST"])
def update_fillups(request):
    """
        Update fillups for a user
    """
    user = request.user
    fillup_multiplier = request.data.get("fillup_multiplier")
    fillup_is_active = request.data.get("fillup_is_active")

    total_savings, c = UserTotalSavings.objects.get_or_create(user=user)

    total_savings.fillup_multiplier = fillup_multiplier
    total_savings.fillup_is_active = fillup_is_active
    total_savings.save()

    return Response(make_response("Fillups updated successfully", data=UserTotalSavingsSerializer(total_savings).data))
