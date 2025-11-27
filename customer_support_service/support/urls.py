from django.urls import path
from . import views

urlpatterns = [
    # Chat endpoints
    path('chat', views.send_message, name='send_message'),
    path('sessions', views.get_sessions, name='get_sessions'),
    path('history/<uuid:session_id>', views.get_session_history, name='get_session_history'),
    path('sessions/<uuid:session_id>/close', views.close_session, name='close_session'),
    
    # Info endpoints
    path('info', views.chatbot_info, name='chatbot_info'),
    path('health', views.health_check, name='health_check'),
]
