"""URL routing configuration for the authentication API.

This module maps incoming HTTP request paths to their respective registration 
and login API views, and includes built-in authentication routes provided 
by the Django REST Framework.
"""

from django.urls import include, path
from .views import RegisterView, LoginView

# Global URL patterns list for the auth application.
# Maps specific endpoints to their class-based views or included routers.
urlpatterns = [
    path('registration/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    # Built-in DRF login/logout views for the browsable API interface.
    path('api-auth/', include('rest_framework.urls')),
]
