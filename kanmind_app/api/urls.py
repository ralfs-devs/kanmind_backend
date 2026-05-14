from django.urls import path
from .views import BoardsViewSet, TasksViewSet, EmailCheckView
urlpatterns = [
    path('boards/',
         BoardsViewSet.as_view({'get': 'list', 'post': 'create'}), name='boards-list'),
    path('boards/<int:pk>/', BoardsViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='boards-detail'),
    path('tasks/',
         TasksViewSet.as_view({'get': 'list', 'post': 'create'}), name='tasks-list'),
    path('tasks/<int:pk>/', TasksViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='tasks-detail'),
    path('email-check/',
         EmailCheckView.as_view(), name='email-check')

]
