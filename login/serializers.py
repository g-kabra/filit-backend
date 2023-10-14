from django.contrib.auth import get_user_model

from rest_framework import serializers

from login.models import UserDailySavings, UserTotalSavings, FillUp


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }

    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.create_user(**validated_data)
        return user

class DailySavingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDailySavings
        fields = '__all__'

class UserTotalSavingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTotalSavings
        fields = '__all__'

class FillUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = FillUp
        fields = '__all__'