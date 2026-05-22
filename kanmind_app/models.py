from django.db import models
from user_auth_app.models import UserProfile

# Create your models here.


class Boards(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        "user_auth_app.UserProfile", on_delete=models.CASCADE, related_name="boards_owner")
    members = models.ManyToManyField(
        "user_auth_app.UserProfile", related_name="boards_members")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Boards'


class Tasks(models.Model):
    # Status-Choices
    TO_DO = 'to-do'
    IN_PROGRESS = 'in-progress'
    REVIEW = 'review'
    DONE = 'done'
    STATUS_CHOICES = [
        (TO_DO, 'to-do'),
        (IN_PROGRESS, 'in-progress'),
        (REVIEW, 'review'),
        (DONE, 'done'),
    ]

    # Priority-Choices
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    PRIORITY_CHOICES = [
        (LOW, 'low'),
        (MEDIUM, 'medium'),
        (HIGH, 'high'),
    ]

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
        return self.title

    class Meta:
        verbose_name_plural = 'Tasks'


class Comments(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="comments_user")
    task = models.ForeignKey(
        Tasks, on_delete=models.CASCADE, related_name="comments_task")

    class Meta:
        verbose_name_plural = 'Comments'
