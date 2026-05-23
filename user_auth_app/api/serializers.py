from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate, get_user_model

from ..models import UserProfile

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """Serializer handling user registration and token generation.

    Validates that incoming data contains only allowed fields, ensures passwords
    match, checks for email uniqueness, and handles user instance creation
    along with an authentication token.

    Attributes:
        fullname (serializers.CharField): The full name of the user.
        email (serializers.EmailField): The unique email used for identification.
        password (serializers.CharField): Write-only field for the account password.
        repeated_password (serializers.CharField): Write-only field to confirm the password.
    """
    fullname = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def to_internal_value(self, data):
        """Validates input payload keys before parsing field values.

        Strictly rejects payloads containing fields not defined in the serializer
        to prevent mass-assignment vulnerabilities.

        Args:
            data (dict): The raw, unvalidated input data from the request.

        Returns:
            dict: The parsed and validated primitive data values.

        Raises:
            serializers.ValidationError: If any unknown fields are present in the data.
        """
        allowed_fields = set(self.fields.keys())
        provided_fields = set(data.keys())
        unknown_fields = provided_fields - allowed_fields
        if unknown_fields:
            raise serializers.ValidationError(
                {field: "This field is not allowed." for field in unknown_fields}
            )
        return super().to_internal_value(data)

    def validate(self, data):
        """Performs cross-field validation for registration rules.

        Checks if the provided passwords are identical and verifies that the
        requested email address is not already registered in the system.

        Args:
            data (dict): Dictionary of field values parsed by to_internal_value.

        Returns:
            dict: The cleaned and validated data dictionary.

        Raises:
            serializers.ValidationError: If passwords mismatch or email is taken.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                "Passwords do not match.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return data

    def create(self, validated_data):
        """Creates a new UserProfile instance and an associated Auth Token.

        Removes the redundant confirmation password before calling the custom
        user manager to securely persist the record.

        Args:
            validated_data (dict): Validated data from the serializer fields.

        Returns:
            UserProfile: The newly created user profile instance.
        """
        validated_data.pop('repeated_password')
        user = UserProfile.objects.create_user(
            email=validated_data['email'],
            fullname=validated_data['fullname'],
            password=validated_data['password']
        )

        Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer handling user authentication credentials.

    Validates that incoming data contains only allowed fields and checks
    credentials against Django's authentication system to verify the user.

    Attributes:
        email (serializers.EmailField): The login email address.
        password (serializers.CharField): Write-only field for the login password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def to_internal_value(self, data):
        """Validates input payload keys before parsing login credentials.

        Ensures no extra or unexpected data is transmitted in the login request.

        Args:
            data (dict): The raw, unvalidated input data from the request.

        Returns:
            dict: The parsed and validated primitive data values.

        Raises:
            serializers.ValidationError: If any unknown fields are present in the data.
        """
        allowed_fields = set(self.fields.keys())
        provided_fields = set(data.keys())
        unknown_fields = provided_fields - allowed_fields
        if unknown_fields:
            raise serializers.ValidationError(
                {field: "This field is not allowed." for field in unknown_fields}
            )
        return super().to_internal_value(data)

    def validate(self, data):
        """Authenticates user credentials using Django's built-in framework.

        Verifies the email and password combination, appending the authenticated
        user instance to the validated data if successful.

        Args:
            data (dict): Dictionary of field values parsed by to_internal_value.

        Returns:
            dict: The validated data dictionary, now including the authenticated user object.

        Raises:
            serializers.ValidationError: If authentication fails due to invalid credentials.
        """
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Wrong email or password.")
        data['user'] = user
        return data
