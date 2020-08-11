from django.contrib.auth.views import LoginView
from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.ProfilePage.as_view(), name='profile'),
]
