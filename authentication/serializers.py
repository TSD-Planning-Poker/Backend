
from rest_framework import serializers
from django.contrib.auth.models import AbstractUser, User


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
