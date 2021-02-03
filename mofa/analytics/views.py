# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import requests

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User

from analytics.src.engagementTimeAnalytics.analyseTimeOnPage import analyseModuleVisitTime
from analytics.src.genericAnalytics import analytics
from analytics.src.participationAnalytics import distinctPageViews
from analytics.src.participationAnalytics import assignmentParticipation
from analytics.src.participationAnalytics import quizParticipation
from analytics.src.dtAnalytics import dtStudentAnalytics
from analytics.src.dtAnalytics import dtPageViewAnalytics
from analytics.src import lrsConnect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException

# When using function based views instead of class based views
#
# from rest_framework.decorators import api_view
# from rest_framework.decorators import permission_classes

from django.shortcuts import render


class StandardResponse(APIView):
    """
    View to return a default response and default response code.
    Requires the request to be (Token)Authenticated
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(f'Hello, this is the default response {Response.status_code}')


class ParameterResponse(APIView):
    """
    View to return a default response together with the entered parameters.
    Requires the request to be (Token)Authenticated
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, parameters):
        return Response(f'Hello, this is a response with the following arguments: {parameters}')


class ViewedCountAnalytics(APIView):
    """
    View to return the total amount of viewed statements in the LRS
    Requires the request to be (Token)Authenticated
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, courseid):
        value = analytics.countViewedStatements(courseid)
        return Response(value)


class AllStatements(APIView):
    """
    View to return a Json object of all the statements in the LRS
    Requires the request to be (Token)Authenticated
    Uses a HTTP get request to get all the statements in the LRS
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        url = 'http://box.science.uu.nl:8001//data/xAPI/statements/'
        content = 'application/json'
        xApiVersion = '1.0.3'
        auth = 'YTA0Yzk2NTNlNjUwZjYzMTQ5YThhODM2MGVlYmY5NjgwM2U3MmNjNzo4YTlkODJlZjZjNDkwNmExYTIxMjhjZDljYzA2ZWM4MDU4NTA1NWM1'
        headers = {'Content-type': content, 'X-Experience-API-Version': xApiVersion, 'Authorization': 'Basic %s' % auth}
        response = requests.get(url, headers=headers)
        return Response(response.json())


class ViewedHistory(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, courseid):
        response = analytics.generateViewedHistory(courseid)
        return Response(response)


class EngagementTime(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, courseID):
        response = analyseModuleVisitTime(courseID)
        return Response(response)


class DistinctPageViews(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, courseid):
        response = distinctPageViews.generateData(courseid)
        return Response(response)


class AssignmentParticipation(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, courseid):
        response = assignmentParticipation.generateData(courseid)
        return Response(response)


class QuizParticipation(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, courseid):
        response = quizParticipation.generateData(courseid)
        return Response(response)


class DTbetweenStudents(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, scenarioID):
        response = dtStudentAnalytics.betweenStudentsDifference(scenarioID)
        return Response(response)


class DTbetweenStudentAttempts(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, scenarioID):
        response = dtStudentAnalytics.betweenStudentAttemptDifference(scenarioID)
        return Response(response)


class DTbestAttempts(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, scenarioID):
        response = dtStudentAnalytics.bestAttemptStatistics(scenarioID)
        return Response(response)


class DTpageViews(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, scenarioID, courseid):
        response = dtPageViewAnalytics.dtViewedPages(scenarioID, courseid)
        return Response(response)
