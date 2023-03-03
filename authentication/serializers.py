from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import customUser


class customUserSerializer(serializers.ModelSerializer):
    class Meta:
        User = get_user_model()
        model = User
        fields = [
            "email",
            "password",
            "mobile",
            "first_name",
            "last_name",
            "dob",
        ]

        def create(self, **validated_data):
            User = get_user_model()
            user = User.objects.create_user(**validated_data)
            return user
