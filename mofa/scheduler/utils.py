# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Utility functions used by multiple scheduler/ scripts."""
from courses.models import Course
import assistants.moodle as moodle_api
import datetime as dt


def get_course_from_db(course_id):
    """Returns the Course object while error handling.

    :param course_id: ID of the course of the course object to retrieve from the database.
    :type course_id: int
    :return: Requested Course object
    :rtype: courses.models.Course
    """

    try:
        return Course.objects.get(courseId=course_id)
    except Course.DoesNotExist:
        print("Course: " + str(course_id) + " could not be found in Course when searched in get_course_from_db")
        return None
    except Course.MultipleObjectsReturned:
        print("Course: " + str(course_id) + " has multiple entries in Course when searched in get_course_from_db")
        return None


def check_if_ended(id):
    """
    Check if the course has already ended.

    :param id: Id of the course that needs to be checked.
    :type id: int
    :return: If a course has ended
    :rtype: bool
    """

    course = moodle_api.get_course_by_id_field(id)
    end_date = course['courses'][0]['enddate']
    if(dt.datetime.fromtimestamp(end_date) < dt.datetime.today()):
        return True
    else:
        return False
