from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer, LoginSerializer


class RegisterView(APIView):
    """API view handling user registration.

    Endpoints using this view are publicly accessible and process incoming
    registration data to create new user accounts along with authentication tokens.

    Attributes:
        permission_classes (list): Permissions required to access this view.
            Defaults to [AllowAny].
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Processes a POST request to register a new user profile.

        Validates the request payload against the RegisterSerializer. If valid,
        creates the user record and returns the generated authentication token
        along with primary profile information.

        Args:
            request (rest_framework.request.Request): The incoming HTTP request
                containing the registration payload in `request.data`.

        Returns:
            rest_framework.response.Response: A response object containing:
                - On Success (201 Created): A dictionary with 'token', 'fullname',
                  'email', and 'user_id'.
                - On Failure (400 Bad Request): A dictionary containing field-specific
                  validation errors.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'token': user.auth_token.key,
                'fullname': user.fullname,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """API view handling user authentication.

    Endpoints using this view are publicly accessible and verify user credentials
    to provide an authentication token for subsequent authorized requests.

    Attributes:
        permission_classes (list): Permissions required to access this view.
            Defaults to [AllowAny].
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Processes a POST request to authenticate an existing user.

        Validates credentials against the LoginSerializer. If authentication
        is successful, retrieves the user profile and returns the active auth token
        along with user profile data.

        Args:
            request (rest_framework.request.Request): The incoming HTTP request
                containing login credentials in `request.data`.

        Returns:
            rest_framework.response.Response: A response object containing:
                - On Success (200 OK): A dictionary with 'token', 'fullname',
                  'email', and 'user_id'.
                - On Failure (400 Bad Request): A dictionary containing validation or
                  authentication error messages.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({
                'token': user.auth_token.key,
                'fullname': user.fullname,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
