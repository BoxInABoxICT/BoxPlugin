# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Configure how Django processes http requests."""
from django.urls import path

from . import views

urlpatterns = [
    path('api/new_activity_notification/<int:action_id>/', views.new_activity_notification,
         name='new_activity_notification'),
    path('api/course_sync_agent/', views.course_sync_agent_execute, name='course_sync_agent'),
    path('api/user_sync_agent/', views.user_sync_agent_execute, name='user_sync_agent'),
    path('api/question_sync_agent/', views.question_sync_agent_execute, name='question_sync_agent'),
    path('api/quiz_completed_feedback/<int:action_id>/', views.quiz_completed_feedback, name='quiz_completed_feedback')
]
