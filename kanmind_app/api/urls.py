"""URL routing configuration for the core application API.

This module maps endpoints for the management of Kanban boards, tasks, 
comments, and utility features like email checking to their respective 
viewsets and class-based views.
"""

from django.urls import path
from .views import BoardsViewSet, TasksViewSet, EmailCheckView, CommentsViewSet

# Global URL patterns list for the core application.
# Configures RESTful resource paths and binds HTTP methods to ViewSet actions.
urlpatterns = [
    # Boards URLs
    path('boards/',
         BoardsViewSet.as_view({'get': 'list', 'post': 'create'}), name='boards-list'),
    path('boards/<int:pk>/', BoardsViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='boards-detail'),

    # Email Check URL
    path('email-check/',
         EmailCheckView.as_view(), name='email-check'),

    # Tasks URLs
    path('tasks/',
         TasksViewSet.as_view({'get': 'list', 'post': 'create'}), name='tasks-list'),
    path('tasks/assigned-to-me/',
         TasksViewSet.as_view({'get': 'assigned_to_me'}), name='tasks-assigned-to-me'),
    path('tasks/reviewing/',
         TasksViewSet.as_view({'get': 'reviewed_by_me'}), name='tasks-reviewed-by-me'),
    path('tasks/<str:pk>/', TasksViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='tasks-detail'),
    path('tasks/<int:task_id>/comments/',
         CommentsViewSet.as_view({'get': 'list', 'post': 'create'}), name='task-comments-list'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/',
         CommentsViewSet.as_view({'delete': 'destroy'}), name='task-comment-delete'),
]
