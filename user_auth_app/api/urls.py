
from django.urls import include, path
from .views import RegisterView, LoginView

urlpatterns = [
    path('registration/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    path('api-auth/', include('rest_framework.urls')),
]
