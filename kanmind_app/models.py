from django.db import models
from user_auth_app.models import UserProfile


class Boards(models.Model):
    """Represents a project board that contains tasks and belongs to an owner.

    Attributes:
        title (str): The name or title of the board.
        owner (ForeignKey): The user profile that owns and manages the board.
        members (ManyToManyField): User profiles assigned as members to the board.
    """
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        "user_auth_app.UserProfile", on_delete=models.CASCADE, related_name="boards_owner")
    members = models.ManyToManyField(
        "user_auth_app.UserProfile", related_name="boards_members")

    def __str__(self):
        """Return the string representation of the board.

        Returns:
            str: The title of the board.
        """
        return self.title

    class Meta:
        verbose_name_plural = 'Boards'


class Tasks(models.Model):
    """Represents an individual task or ticket within a specific board.

    Attributes:
        board (ForeignKey): The board this task belongs to.
        title (str): The concise title of the task.
        description (str): Detailed text describing the task requirements.
        status (str): Current workflow state (e.g., 'to-do', 'done').
        priority (str): Urgency level of the task (e.g., 'low', 'high').
        assignee (ForeignKey): The user profile responsible for executing the task.
        reviewer (ForeignKey): The user profile responsible for reviewing the task.
        due_date (date): The deadline date for task completion.
    """

    TO_DO = 'to-do'
    IN_PROGRESS = 'in-progress'
    REVIEW = 'review'
    DONE = 'done'

    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

    # Create status choices tupel and
    # replace dashes with blanks in labels (for better readablity).
    STATUS_CHOICES = [(val, val.replace('-', ' '))
                      for val in (TO_DO, IN_PROGRESS, REVIEW, DONE)]

    # Create  Priority Choices tupel
    PRIORITY_CHOICES = [(val, val) for val in (LOW, MEDIUM, HIGH)]

    board = models.ForeignKey(
        Boards, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=TO_DO)
    priority = models.CharField(
        max_length=50, choices=PRIORITY_CHOICES, default=MEDIUM)
    assignee = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                                 related_name="tasks_assignee", default=1)
    reviewer = models.ForeignKey(UserProfile, on_delete=models.PROTECT,
                                 related_name="tasks_reviewer", default=1)
    due_date = models.DateField()

    def __str__(self):
        """Return the string representation of the task.

        Returns:
            str: The title of the task.
        """
        return self.title

    class Meta:
        verbose_name_plural = 'Tasks'


class Comments(models.Model):
    """Represents a text comment left by a user on a specific task.

        Attributes:
            content (str): The body text of the comment.
            created_at (datetime): Automatically set timestamp when created.
            author (ForeignKey): The user profile who wrote the comment.
            task (ForeignKey): The task this comment is attached to.
        """
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="comments_user")
    task = models.ForeignKey(
        Tasks, on_delete=models.CASCADE, related_name="comments_task")

    def __str__(self):
        """Return the string representation of the comment.

        Returns:
            str: The content text snippet of the comment.
        """
        return self.content

    class Meta:
        verbose_name_plural = 'Comments'
