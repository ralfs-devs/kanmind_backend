from user_auth_app.models import UserProfile
from django.contrib.auth import get_user_model
from ..models import Boards, Tasks
from rest_framework import serializers

User = get_user_model()


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for the Boards model to handle summary views.

    Provides high-level statistics about a board, including member and task counts,
    and handles adding members via primary keys.
    """
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
        """Calculate the total number of members assigned to the board.

        Args:
            obj (Boards): The board instance being serialized.

        Returns:
            int: Total number of board members.
        """
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Calculate the total number of tasks associated with the board.

        Args:
            obj (Boards): The board instance being serialized.

        Returns:
            int: Total number of tasks.
        """
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Calculate the number of tasks with a 'TO_DO' status on the board.

        Args:
            obj (Boards): The board instance being serialized.

        Returns:
            int: Number of pending tasks.
        """
        return obj.tasks.filter(status=Tasks.TO_DO).count()

    def get_tasks_high_prio_count(self, obj):
        """Calculate the number of tasks with a 'HIGH' priority on the board.

        Args:
            obj (Boards): The board instance being serialized.

        Returns:
            int: Number of high priority tasks.
        """
        return obj.tasks.filter(priority=Tasks.HIGH).count()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information."""

    class Meta:
        model = UserProfile
        fields = ['id', 'email', 'fullname']

    def validate_email(self, value):
        """Validate that the given email exists in the database.

        Performs a case-insensitive lookup to confirm the email is valid.

        Args:
            value (str): The email address to validate.

        Returns:
            str or None: The validated email address if found, otherwise None.
        """
        if UserProfile.objects.filter(email__iexact=value).exists():
            return value
        return None


class SingleBoardSerializer(serializers.ModelSerializer):
    """Serializer for detailed view of a single board.

    Includes full nested member profiles and a custom list of tasks 
    excluding their parent board ID to avoid redundant data.
    """
    members = UserProfileSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()
    owner_id = serializers.PrimaryKeyRelatedField(
        read_only=True, source='owner')

    def get_tasks(self, obj):
        """Retrieve and serialize tasks with prefetched comments.

        Removes the 'board' key from individual task structures for a cleaner payload.

        Args:
            obj (Boards): The board instance being serialized.

        Returns:
            list[dict]: A list of serialized task objects without the board field.
        """
        tasks = obj.tasks.prefetch_related('comments_task').all()
        context = {**self.context, 'from_board': True}
        serializer = TasksSerializer(tasks, many=True, context=context)

        data = serializer.data
        for task_data in data:
            task_data.pop('board', None)
        return data

    class Meta:
        model = Boards
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class TasksSerializer(serializers.ModelSerializer):
    """Serializer for handling task CRUD operations.

    Enforces dynamic validation rules based on the request method, preventing
    tasks from migrating to other boards during updates and managing nested comments.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the serializer and set the board field to read-only for updates."""
        super().__init__(*args, **kwargs)
        if self.context.get('request') and self.context.get('request').method in ['PUT', 'PATCH']:
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

    def get_extra_kwargs(self):
        """Dynamically adjust field requirements based on the instance state.

        Forces description, status, priority, and board fields to be required
        during task creation (POST).

        Returns:
            dict: The updated dictionary of extra keyword arguments.
        """
        kwargs = super().get_extra_kwargs()

        if self.instance is None:
            for field_name in ['description', 'status', 'priority', 'board']:
                kwargs.setdefault(field_name, {})
                kwargs[field_name]['required'] = True
        return kwargs

    def get_comments_count(self, obj):
        """Count the comments associated with the task efficiently via database.

        Args:
            obj (Tasks): The task instance being serialized.

        Returns:
            int: The total count of comments for this task.
        """
        return obj.comments_task.count()

    def to_internal_value(self, data):
        """Validate input data and strip board updates for existing records.

        Ensures that tasks cannot be transferred to a different board during updates.

        Args:
            data (dict): The raw, unvalidated input data.

        Returns:
            dict: The validated internal value dictionary.
        """
        if self.context.get('request') and self.context.get('request').method in ['PUT', 'PATCH']:
            data.pop('board', None)
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """Format the outgoing JSON payload.

        Removes the board information during update operations (PUT/PATCH).

        Args:
            instance (Tasks): The task model instance.

        Returns:
            dict: The serialized dictionary representation of the task.
        """
        data = super().to_representation(instance)
        if self.context.get('request') and self.context.get('request').method in ['PUT', 'PATCH']:
            data.pop('board', None)
        return data

    def get_comments(self, obj):
        """Serialize comments assigned to this task with formatted timestamps.

        Args:
            obj (Tasks): The task instance being serialized.

        Returns:
            list[dict]: A list of comments containing id, created_at, author, and content.
        """
        return [
            {
                "id": c.id,
                "created_at": c.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "author":  c.author.user.username,
                "content": c.content
            }
            for c in obj.comments_task.all()
        ]
