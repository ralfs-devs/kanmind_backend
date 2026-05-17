
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import Boards, Tasks
from .serializers import BoardSerializer, EmailCheckSerializer, TasksSerializer, SingleBoardSerializer
from .permissions import IsBoardOwner

User = get_user_model()


class BoardsViewSet(viewsets.ModelViewSet):
    queryset = Boards.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Verwendet SingleBoardSerializer für 'retrieve' (GET /boards/123/)
        if self.action == 'retrieve':
            return SingleBoardSerializer  # Gibt SingleBoardSerializer zurück
        return super().get_serializer_class()

    def perform_create(self, serializer):
        # Speichert das Board, Owner ist der aktuelle Benutzer
        board = serializer.save(owner=self.request.user)
        # Fügt die übergebenen Mitglieder aus dem Request-Body hinzu
        member_ids = self.request.data.get('members', [])
        board.members.set(member_ids)

    def perform_destroy(self, instance):
        if not IsAuthenticated():
            raise permissions.PermissionDenied(
                "Authentication required to delete a board.", status=status.HTTP_401_UNAUTHORIZED)
        elif not IsBoardOwner():
            raise permissions.forbidden(
                "Only the board owner can delete this board.", status=status.HTTP_403_FORBIDDEN)
        elif instance is None:
            return Response(
                "Board not found.", status=status.HTTP_404_NOT_FOUND)

        instance.delete()
        return self.response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        user = self.request.user
        # Gibt Boards zurück, bei denen der Benutzer Owner oder Member ist
        return Boards.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()


class EmailCheckView(APIView):
    queriset = User.objects.all()
    serializers_class = EmailCheckSerializer
    permission_classes = [IsAuthenticated]

    if not IsAuthenticated():
        raise permissions.PermissionDenied(
            "Nicht authentifiziert. Der Benutzer muss eingeloggt sein.", status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request):
        email = request.query_params.get('email').strip()
        if not email:
            return Response("E-mail-Adresse fehlt", status=400)
        try:
            validate_email(email)
        except ValidationError:
            return Response("Ungültiges E-Mail-Format", status=400)
        try:
            user = User.objects.get(email__iexact=email)
            return Response({
                'id': user.id,
                'email': user.email,
                'fullname': user.fullname
            })

        except User.DoesNotExist:
            return Response("Email nicht gefunden. Es gibt keinen aktiven Benutzer mit dieser Email.", status=status.HTTP_404_NOT_FOUND)


class TasksViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TasksSerializer
    permission_classes = [IsAuthenticated]
