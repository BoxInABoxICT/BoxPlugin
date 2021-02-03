# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
from django.urls import path

from . import views

# Mapping between URL path expressions to Python view functions
urlpatterns = [
    path('engagementTime/<str:courseID>',
         views.EngagementTime.as_view(), name='EngagementTimeAnalytics'),
    path('viewed/count/<int:courseid>', views.ViewedCountAnalytics.as_view(), name='viewedCountAnalytics'),
    path('statements', views.AllStatements.as_view(), name='viewsStatements'),
    path('<str:parameters>', views.ParameterResponse.as_view(), name='parameterResponse'),
    path('', views.StandardResponse.as_view(), name='standardResponse'),
    path('viewed/history/<str:courseid>', views.ViewedHistory.as_view(), name='viewedHistory'),
    path('participation/page/<str:courseid>', views.DistinctPageViews.as_view(), name='pageParticipation'),
    path('participation/assignment/<str:courseid>', views.AssignmentParticipation.as_view(), name='assignmentParticipation'),
    path('participation/quiz/<str:courseid>', views.QuizParticipation.as_view(), name='quizParticipation'),
    path('dt/betweenstudents/<int:scenarioID>', views.DTbetweenStudents.as_view(), name='dt_betweenStudents'),
    path('dt/betweenstudentattempts/<int:scenarioID>', views.DTbetweenStudentAttempts.as_view(), name='dt_betweenStudentAttempts'),
    path('dt/bestattempts/<int:scenarioID>', views.DTbestAttempts.as_view(), name='dt_bestAttempts'),
    path('dt/pageviews/<int:scenarioID>/<str:courseid>', views.DTpageViews.as_view(), name='dt_pageViews'),
]
