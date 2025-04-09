from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('chatbot/', views.chatbot_page, name='chatbot'),
    path('chat-api/', views.chatbot, name='chat-api'),  # API endpoint for processing chat messages
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
