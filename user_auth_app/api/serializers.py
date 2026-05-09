from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..models import UserProfile


class RegisterSerializer(serializers.Serializer):
    fullname = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                "Passwörter stimmen nicht überein.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                "Ein Benutzer mit dieser E-Mail existiert bereits.")
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserProfile.objects.create(
            user=user,
            fullname=validated_data['fullname']
        )
        Token.objects.create(user=user)
        return user
