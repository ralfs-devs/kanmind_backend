from user_auth_app.models import UserProfile
from django.contrib.auth import get_user_model
from ..models import Boards, Tasks
from rest_framework import serializers


User = get_user_model()


class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(), many=True, required=False
    )
    owner_id = serializers.PrimaryKeyRelatedField(
        source='owner', read_only=True)

    class Meta:
        model = Boards
        fields = [
            'id', 'title', 'members', 'member_count',
            'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id'
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()  # Zählt alle Tasks für dieses Board

    def get_tasks_to_do_count(self, obj):
        # Zählt Tasks mit Status "To Do"
        return obj.tasks.filter(status=Tasks.TO_DO).count()

    def get_tasks_high_prio_count(self, obj):
        # Zählt Tasks mit hoher Priorität
        return obj.tasks.filter(priority=Tasks.HIGH).count()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'email', 'fullname']


class SingleBoardSerializer(serializers.ModelSerializer):
    members = UserProfileSerializer(many=True, read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        read_only=True, source='owner')

    class Meta:
        model = Boards
        fields = ['id', 'title', 'members', 'owner_id']


class EmailCheckSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = UserProfile
        fields = ['id', 'email', 'fullname']

    def validate_email(self, value):
        # Prüfen, ob die E-Mail-Adresse bereits existiert
        if UserProfile.objects.filter(email__iexact=value).exists():
            return value
        return (None)


class TasksSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tasks
        fields = ['id', 'board', 'title', 'description', 'status',
                  'priority', 'assignee', 'reviewer', 'due_date']
