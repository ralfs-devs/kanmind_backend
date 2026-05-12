from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from kanmind_app.models import Boards, Tasks
from .serializers import BoardsSerializer, TasksSerializer, SingleBoardSerializer


class BoardsViewSet(viewsets.ModelViewSet):
    queryset = Boards.objects.all()
    serializer_class = BoardsSerializer
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

    def get_queryset(self):
        user = self.request.user
        # Gibt Boards zurück, bei denen der Benutzer Owner oder Member ist
        return Boards.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()


class TasksViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TasksSerializer
    permission_classes = [IsAuthenticated]
