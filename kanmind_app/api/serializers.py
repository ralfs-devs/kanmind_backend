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
        queryset=UserProfile.objects.all(), many=True, required=True, write_only=True
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
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status=Tasks.TO_DO).count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority=Tasks.HIGH).count()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'email', 'fullname']

    def validate_email(self, value):
        email = serializers.EmailField()
        if UserProfile.objects.filter(email__iexact=value).exists():
            return value
        return (None)


class SingleBoardSerializer(serializers.ModelSerializer):
    members = UserProfileSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()
    owner_id = serializers.PrimaryKeyRelatedField(
        read_only=True, source='owner')

    def get_tasks(self, obj):
        tasks = obj.tasks.prefetch_related('comments_task').all()
        context = {**self.context, 'from_board': True}
        serializer = TasksSerializer(tasks, many=True, context=context)

    # down't show the board id in serialized data:
        data = serializer.data
        for task_data in data:
            task_data.pop('board', None)
        return data

    class Meta:
        model = Boards
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class TasksSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for updates, make 'board' read-only:
        if self.context.get('request').method in ['PUT', 'PATCH']:
            self.fields['board'].read_only = True
    comments_count = serializers.SerializerMethodField()
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(),
        source='assignee',
        write_only=True
    )
    assignee = UserProfileSerializer(read_only=True)

    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(),
        source='reviewer',
        write_only=True
    )

    reviewer = UserProfileSerializer(read_only=True)

    class Meta:
        model = Tasks
        fields = ['id', 'board', 'title', 'description', 'status',
                  'priority', 'assignee', 'reviewer', 'due_date', 'assignee_id', 'reviewer_id', 'comments_count']
        extra_kwargs = {
            'board': {'required': True}
        }

    # Only if a new Dataset shall be saved:
    def get_extra_kwargs(self):
        kwargs = super().get_extra_kwargs()

        if self.instance is None:  # self.instance is None at POST
            for field_name in ['description', 'status', 'priority', 'board']:
                kwargs.setdefault(field_name, {})
                kwargs[field_name]['required'] = True
        return kwargs

    def get_comments_count(self, obj):
        # counts comments effectivly via DB
        return obj.comments_task.count()

    # Tasks may not migrate to another board:
    def to_internal_value(self, data):
        # Make sure board_id is included in the internal value for updates
        if self.context.get('request').method in ['PUT', 'PATCH']:
            data.pop('board', None)
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # delete board only if it's an update, not on create
        # if self.instance is not None:  # self.instance is None on create, see comment above in get_extra_kwargs
        if self.context.get('request').method in ['PUT', 'PATCH']:
            data.pop('board', None)
        return data

    # for getting comments, which are assigned to a task
    def get_comments(self, obj):
        return [
            {
                "id": c.id,
                "created_at": c.created_at.c.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "author":  c.author.user.username,
                "content": c.content
            }
            for c in obj.comments_task.all()
        ]
