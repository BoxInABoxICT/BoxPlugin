# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

# import requests
import json

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework.parsers import JSONParser

from database_API.src.configForms import *
from database_API.src.CourseSettings.courseSettings import fetchCourseSettings, updateCourseSettings
from database_API.src.AssistantActions.assistantSettings import *


class CourseSettings(APIView):
    """
    View handling requests related to Mofa's course settings
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, courseID):
        """
        Fetches current course settings
        """
        form = CourseSettingsForm()
        fetchCourseSettings(courseID, form)
        return Response(form.toJSON())

    def post(self, request, courseID):
        """
        Updates current course settings to the recieved settings
        """
        form = CourseSettingsForm(request.data)
        updateCourseSettings(courseID, form)
        return Response(form.toJSON())


class AssistantSettings(APIView):
    """
    View handling requests related to Mofa's assistants
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, courseID):
        """
        Fetches current course assistants
        """
        ###
        form = AssistantSettingsForm()
        fetchCourseAssistants(courseID, form)
        return Response(form.toJSON())

    def post(self, request, courseID):
        """
        Performs Assistant actions based on the provided request data
        """
        ###
        form = AssistantSettingsForm(request.data)
        updateAssistants(courseID, form)
        return Response(form.toJSON())
