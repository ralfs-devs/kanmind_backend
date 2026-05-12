from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User

from ..models import UserProfile

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    fullname = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def to_internal_value(self, data):
        allowed_fields = set(self.fields.keys())
        provided_fields = set(data.keys())
        unknown_fields = provided_fields - allowed_fields
        if unknown_fields:
            raise serializers.ValidationError(
                {field: "This field is not allowed." for field in unknown_fields}
            )
        return super().to_internal_value(data)

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                "Passwords do not match.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        user = UserProfile.objects.create_user(
            email=validated_data['email'],
            fullname=validated_data['fullname'],
            password=validated_data['password']
        )

        Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def to_internal_value(self, data):
        allowed_fields = set(self.fields.keys())
        provided_fields = set(data.keys())
        unknown_fields = provided_fields - allowed_fields
        if unknown_fields:
            raise serializers.ValidationError(
                {field: "This field is not allowed." for field in unknown_fields}
            )
        return super().to_internal_value(data)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Wrong email or password.")
        data['user'] = user
        return data
