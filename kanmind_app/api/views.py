from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated, ValidationError as DRFValidationError

from ..models import Boards, Tasks, Comments
from .serializers import BoardSerializer, TasksSerializer, SingleBoardSerializer, UserProfileSerializer
from .permissions import IsBoardMember, IsBoardOwner

User = get_user_model()


class BoardsViewSet(viewsets.ModelViewSet):
    queryset = Boards.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated('You are not authenticated')

        lookup_field = self.lookup_field
        lookup_value = self.kwargs[self.lookup_field]

        try:
            obj = Boards.objects.get(**{lookup_field: lookup_value})
        except Boards.DoesNotExist:
            raise Http404("No board found with the given ID.")

        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SingleBoardSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        member_ids = self.request.data.get('members', [])
        board.members.set(member_ids)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        member_ids = request.data.get('members', None)
        if member_ids is not None:
            instance.members.set(member_ids)
        if partial:
            response_data = {
                'id': instance.id,
                'title': instance.title,
                'owner_data': {
                    'id': instance.owner.id,
                    'email': instance.owner.email,
                    'fullname': instance.owner.fullname,
                },
                'members_data': [
                    {
                        'id': member.id,
                        'email': member.email,
                        'fullname': member.fullname
                    } for member in instance.members.all()
                ]
            }
            return Response(response_data)

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'retrieve']:
            return [(IsBoardOwner | IsBoardMember)()]
        if self.action == 'destroy':
            return [(IsBoardOwner)()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        return Boards.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()


class EmailCheckView(APIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response("E-Mail is required", status=400)

        try:
            validate_email(email)
        except ValidationError:
            return Response("Invalid email format", status=400)

        try:
            user = User.objects.get(email__iexact=email)
            return Response({
                'id': user.id,
                'email': user.email,
                'fullname': user.fullname,
            })
        except User.DoesNotExist:
            return Response(
                "Email not found. There is no active user with this email.",
                status=status.HTTP_404_NOT_FOUND,
            )


class TasksViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TasksSerializer
    permission_classes = [IsBoardMember]

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            int(pk)
        except (ValueError, TypeError):
            raise DRFValidationError({'id': 'Must be a number.'})
        return super().get_object()

    def perform_update(self, serializer):
        serializer.save()

        return super().perform_create(serializer)

    def assigned_to_me(self, request):
        # returns all tasks for the authenticated user
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        tasks = Tasks.objects.filter(assignee=user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    def reviewed_by_me(self, request):
        # returns all tasks which the authenticated user shall review
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        tasks = Tasks.objects.filter(reviewer=user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        board_id = request.data.get('board')
        get_object_or_404(Boards, pk=board_id)
        return super().create(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == 'destroy':
            return [(IsBoardOwner | IsBoardMember)()]
        return super().get_permissions()


class CommentsViewSet(viewsets.ViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TasksSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, task_id=None):
        content = request.data.get('content')
        if not content or not content.strip():
            return Response(
                {"content": ["This field is required"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        task = get_object_or_404(Tasks, pk=task_id)
        board = task.board
        if not board.members.filter(pk=request.user.pk).exists():
            return Response(
                {"detail": "You are not member of this board."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            comment = Comments.objects.create(
                content=content.strip(),
                author=request.user,
                task=task
            )
            return Response({
                "id": comment.id,
                "created_at": comment.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "author": comment.author.fullname,
                "content": comment.content
            }, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                {"content": ["Invalid Data."]},
                status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request, task_id=None):
        task = get_object_or_404(Tasks, pk=task_id)
        comments = task.comments_task.all()
        board = task.board
        if not board.members.filter(pk=request.user.pk).exists():
            return Response(
                {"detail": "You are not a member of this board"},
                status=status.HTTP_403_FORBIDDEN
            )

        data = [
            {
                "id": c.id,
                "created_at": c.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "author": c.author.fullname,
                "content": c.content,
            }
            for c in comments
        ]
        return Response(data)

    def destroy(self, request, comment_id=None, task_id=None):

        comment = get_object_or_404(Comments, pk=comment_id)

        task = get_object_or_404(Tasks, pk=task_id)
        board = task.board

        if comment.author != request.user:
            return Response(
                {"detail": "Only the Author is entitled to delete a Comment!"},
                status=status.HTTP_403_FORBIDDEN
            )

        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
