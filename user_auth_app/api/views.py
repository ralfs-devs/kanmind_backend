from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import request, status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..models import UserProfile
from .serializers import RegisterSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    # def get(self, request):
    #     return Response({"message": "Willkommen zum Registrierungsendpunkt. Bitte senden Sie eine POST-Anfrage mit fullname, email, password und repeated_password."})

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = user.profile
            return Response({
                'user_id': user.id,
                'fullname': profile.fullname,
                'email': user.email,
                'token': user.auth_token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
