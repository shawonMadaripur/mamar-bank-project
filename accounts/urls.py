from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserLogoutView, UserUpdateView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name = 'register'),
    path('update/', UserUpdateView.as_view(), name = 'update'),
    path('login/', UserLoginView.as_view(), name = 'login'),
    path('logout/', UserLogoutView, name = 'logout'),
]