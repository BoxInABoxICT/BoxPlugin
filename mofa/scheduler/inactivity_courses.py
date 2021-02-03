# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Handle the inactivity for a course."""
import datetime as dt
import json
import lib.ll_event_parsers
import assistants.learning_locker as ll_api
import assistants.moodle as moodle_api
from scheduler.models import InactivityNotificationSent
from lib.moodle_get_parsers import parse_enrolled_students, parse_course_info
from scheduler.utils import check_if_ended


def create_job(course_id, time_not_active, main_scheduler):
    """
    Call all the methods that are needed to check the inactivity.

    :param course_id: Id of the course the inactivity needs to be checked for.
    :type course_id: int
    :param time_not_active: Time interval the inactivity needs to be checked for.
    :type time_not_active: int
    """
    if(check_if_ended(course_id)):
        main_scheduler.remove_inactivity_notification(course_id)
        return

    time = calculate_date(dt.date.today(), time_not_active)
    if(check_if_older_than(time_not_active, course_id)):
        viewed_courses = ll_api.get_viewed_courses(time, course_id)
        list_viewed = lib.ll_event_parsers.parse_viewed_courses(viewed_courses)
        enrolled_students = parse_enrolled_students(moodle_api.get_enrolled_users(course_id))
        course_name = parse_course_info(moodle_api.get_course_by_id_field(course_id))
        students = students_not_viewed(enrolled_students, list_viewed, course_id)
        message = get_message(course_name, time_not_active)
        if len(students) > 0:
            send_message(students, message)


def check_if_older_than(time_not_active, id):
    """
    Check if the course was created before the time for which inactivity is checked

    :param id: Id of the course that needs to be checked.
    :type id: int
    :param time_not_active: Number of days of inactivity.
    :type time_not_active: int
    :return: If a course was created before
    :rtype: bool
    """
    course = moodle_api.get_course_by_id_field(id)
    time_created = course['courses'][0]['timecreated']
    date_created = dt.date.fromtimestamp(time_created)
    difference = (dt.date.today() - date_created).days
    if(difference < time_not_active):
        return False
    else:
        return True


def calculate_date(date_today, time_not_active):
    """
    Calculate the date since when the inactivity needs to be checked for.

    :param date_today: Today's date.
    :type date_today: date
    :param time_not_active: Number of days of inactivity.
    :type time_not_active: int
    :return: Date that a message should be sent.
    :rtype: int
    """
    return date_today - dt.timedelta(days=time_not_active)


def get_database_object(course_id, error_on_not_found=True):
    """
    Get the database entry and handle the does not exist error

    :param course_id: The id of the course.
    :type course_id: int
    :param error_on_not_found: Whether the course exist in the database
    :type error_on_not_found: bool
    :return: database entry
    :rtype: object
    """
    try:
        return InactivityNotificationSent.objects.get(pk=course_id)
    except Exception as e:
        print(e)
        if error_on_not_found:
            print("Course: " + str(course_id) + " could not be found in InactivityNotificationSent when searched in get_database_object")
        return None


def students_not_viewed(students, list_viewed, course_id):
    """
    Determine which students need to be send a message.

    :param students: List of the enrolled students.
    :type students: list(str)
    :param list_viewed: List of the students who have viewed a course
    :type list_viewed: list(str)
    :return: A list of student ids.
    :rtype: list(str)
    """
    # Get students which already have gotten a notification
    database_entry = get_database_object(course_id)
    if database_entry is None:
        new_entry = InactivityNotificationSent(str(course_id), '{}')
        database_entry = new_entry
    student_id_dict = json.loads(database_entry.args_json)
    student_id_set = set(student_id_dict.keys())
    student_send_notification = list(set(students) - set(list_viewed).union(student_id_set))
    for student_id in student_send_notification:
        student_id_dict[student_id] = 1
    database_entry.args_json = json.dumps(student_id_dict)
    database_entry.save()
    return student_send_notification


def get_message(course_name, time_not_active):
    """
    Format the message that needs to be send.

    :param course_name: The name of the course.
    :type course_name: str
    :param time_not_active: Time that a student has not been active.
    :type time_not_active: int
    :return: Message to be send to users.
    :rtype: str
    """
    message = f'You have not viewed the course "{course_name}" in {time_not_active} day(s). ' \
              f'We advise you to stay active, so that you will not miss anything.'
    return message


def send_message(students, message):
    """
    Loop over the list of student ids, and send a message to every student in the list.

    :param students: List of student ids.
    :type students: list(str)
    :param message: The message that needs to be send.
    :type message: str
    """
    students = set(students)
    moodle_api.send_bulk_messages(students, message)
