# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

import json

from courses.models import Course
from assistants.models import NewActivityCreated


def fetchNewActivityAssistant(CourseID):
    """
    Queries the mofa database to search for the assistant associated with the course ID
    :courseID: Moodle ID for the course to which the assistand is related. \t
    :type: str \n
    :returns: the created Assistant Model instance if assistant was found in the database, None otherwise \t
    :rtype: Assistant \n
    """
    c = Course.objects.get(courseId=CourseID)
    try:
        assistant = NewActivityCreated.objects.get(course_id=c.id)
        return assistant
    except Exception:
        return None


def createNewActivityAssistant(courseID):
    """
    Adds a new NewActivityAssistant to the mofa database.
    :courseID: Moodle ID for the course to which the assistand is related. \t
    :type: str \n
    :returns: the created Assistant Model instance if the add was successfull, None otherwise \t
    :rtype: Assistant \n
    """
    try:
        c = Course.objects.get(courseId=courseID)
        assistant = NewActivityCreated.objects.create(course=c)
        assistant.save()
        return assistant
    except Exception:
        return None


def deleteNewActivityAssistant(courseID):
    """
    Deletes the specified assistant from the course.
    :courseID: Moodle ID for the course to which the assistand is related. \t
    :type: str \n
    :assistantID: Mofa ID of the assistant to delete. \t
    :type: str \n
    :returns: the created Assistant Model instance that was deleted, None otherwise \t
    :rtype: Assistant \n
    """
    c = Course.objects.get(courseId=courseID)
    try:
        assistant = NewActivityCreated.objects.get(course_id=c.id)
        assistant.delete()
        return assistant
    except Exception:
        return None
