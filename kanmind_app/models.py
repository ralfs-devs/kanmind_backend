from django.db import models
from user_auth_app.models import UserProfile

# Create your models here.


class Boards(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        "user_auth_app.UserProfile", on_delete=models.CASCADE, related_name="board_owner")
    members = models.ManyToManyField(
        "user_auth_app.UserProfile", related_name="board_members")

    def __str__(self):
        return self.title


class Tasks(models.Model):
    # Status-Choices
    TO_DO = 'to-do'
    IN_PROGRESS = 'in-progress'
    IN_REVIEW = 'in-review'
    DONE = 'done'
    STATUS_CHOICES = [
        (TO_DO, 'To Do'),
        (IN_PROGRESS, 'In Progress'),
        (IN_REVIEW, 'In Review'),
        (DONE, 'Done'),
    ]

    # Priorität-Choices
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    board = models.ForeignKey(
        Boards, on_delete=models.CASCADE, related_name="tasks")
    assignee = models.ManyToManyField(
        "user_auth_app.UserProfile", related_name="task_assignees", blank=True)
    reviewer = models.ForeignKey(
        "user_auth_app.UserProfile", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=TO_DO)
    priority = models.CharField(
        max_length=50, choices=PRIORITY_CHOICES, default=MEDIUM)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title
