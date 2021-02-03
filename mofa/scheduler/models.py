# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Contains all database models."""
from django.db import models


class ProcessedStatement(models.Model):
    """Defines a processed statement."""

    statement_id = models.CharField(max_length=40, primary_key=True)

    class Meta:
        verbose_name = "processed statement"


class FailedStatement(models.Model):
    """Defines a failed statement."""

    statement = models.TextField()
    error = models.CharField(max_length=20)

    class Meta:
        verbose_name = "failed statement"


class CronJob(models.Model):
    """Defines a cron job. This is so that it will be re-added when the server is restarted."""

    JOB_TYPES = (
        ('inactive', 'inactive'),
        ('updatefirstdeadlines', 'updatefirstdeadlines'),
        ('assignment_check', 'assignment_check')
    )

    name = models.CharField(max_length=40, primary_key=True)
    course = models.IntegerField(null=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    # Stores all function parameters as a list, default is an empty list
    args_json = models.TextField(default='undefined')


NOTIFICATION_TYPES = (
    ('early', 'early'),
    ('late', 'late')
)


class AssignmentNotificationSent(models.Model):
    """Stores whether an assignment notification has already been sent."""

    name = models.CharField(max_length=40, primary_key=True)
    assignment_id = models.IntegerField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    time = models.DateTimeField()


class InactivityNotificationSent(models.Model):
    """Stores per course the studentids of the students who have already gotten a notification"""

    course_id = models.IntegerField(primary_key=True)
    args_json = models.TextField(default='{}')


class FirstAssignmentOfCourse(models.Model):
    """Stores per course what the first deadline notifcation is and for which assignment it is."""

    course_id = models.IntegerField(primary_key=True)
    assignment_id = models.IntegerField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    time = models.DateTimeField(null=True)


IGNORED_VERBS = {
    'http://id.tincanapi.com/verb/viewed',
    'http://adlnet.gov/expapi/verbs/answered'
}
