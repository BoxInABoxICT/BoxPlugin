# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

from django.urls import path

from . import views

# Mapping between URL path expressions to Python view functions
urlpatterns = [
    path("courseSettings/<str:courseID>", views.CourseSettings.as_view(), name='CourseSettings'),
    path("AssistantSettings/<str:courseID>", views.AssistantSettings.as_view(), name='AssistantSettings')
]
