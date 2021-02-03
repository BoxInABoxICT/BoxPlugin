# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""This file contains all the requests send to Moodle."""

import requests
from django.conf import settings

from . import logger

URL = settings.MOODLE_WEBSERVICE_URL
TOKEN = settings.MOODLE_TOKEN


class MoodleException(Exception):
    """Moodle exception."""

    pass


def send_message(user_id, message):
    """
    Send a message to one user in Moodle.

    The parameters are defined and used to send a message to Moodle.
    Then, call the function send_query() with the parameters. It handles the actual request to Moodle.
    :param user_id: ID of the user.
    :type user_id: str
    :param message: String text you want to send to the user.
    :type message: str
    """
    send_bulk_messages([user_id], message)


def send_bulk_messages(user_ids, message):
    """
    Send a message to multiple users in Moodle.

    :param user_ids: list of user ids to send the message to
    :type user_ids: list(int)
    :param message: the message to send to the users
    :type message: str
    """
    messages = [(user_id, message) for user_id in user_ids]
    send_bulk_different_messages(messages)


def send_bulk_different_messages(id_messages_list):
    """
    Send multiple different messages to different users.

    :param id_messages_list: list containing tuples (user id, message to send to user)
    :type id_messages_list: list(tuple(str, str))
    """
    func = 'core_message_send_instant_messages'
    messages = [{"touserid": i, "text": m} for (i, m) in id_messages_list]
    data = {"messages": messages}

    send_query(func, data, 200)


def get_course_by_id_field(course_id):
    """
    Get the information of a course.

    The parameters are defined and used to get the course information.
    Then, call the function send_query() with the parameters. It handles the actual request to Moodle.
    :param course_id: Id of a course.
    :type course_id: int
    :return: All the information of the course in JSON.
    :rtype: dict(str, list(dict(str, int)))
    """
    func = 'core_course_get_courses_by_field'
    data = {
        "field": "id",
        "value": course_id
    }

    response = send_query(func, data, 200)
    return response


def get_courses():
    """
    Get all the courses from Moodle.

    :return: All courses from Moodle.
    :rtype: json
    """
    func = 'core_course_get_courses'
    data = {"options": {"ids": []}}

    response = send_query(func, data, 200)
    return response


def get_enrolled_users(course_id):
    """
    Get all the enrolled users of a course.

    The parameters are defined and use all information of the enrolled students of a course.
    Then, call the function send_query() with the parameters. It handles the actual request to Moodle.

    :param course_id: Id of a course.
    :type course_id: str
    :return: All the information of the courses in JSON.
    :rtype: json
    """
    func = 'core_enrol_get_enrolled_users'
    data = {
        "courseid": course_id
    }

    response = send_query(func, data, 200)
    return response


def get_assignments(course_id):
    """
    Request all assignments in a course.

    :param course_id: The course ID.
    :type course_id: str
    :return: JSON containing the assignments.
    :rtype: json
    """
    func = 'mod_assign_get_assignments'
    data = {
        "includenotenrolledcourses": 1,
        "courseids": course_id
    }

    response = send_query(func, data, 200)
    return response


def get_assignment_status(course_id, user_id):
    """
    Request the status of all assignments in a course for a given user.

    :param course_id: The course ID.
    :type course_id: str
    :param user_id: The user ID.
    :type user_id: str
    :return: JSON containing the assignment statuses.
    :rtype: json
    """
    func = 'core_completion_get_activities_completion_status'
    data = {
        "courseid": course_id,
        "userid": user_id
    }

    response = send_query(func, data, 200)
    return response


def get_course_contents(course_id):
    """
    Get all course contents for 1 course from Moodle.

    :param course_id: The course ID.
    :type course_id: str
    :return: JSON containing the course contents.
    :rtype: dict
    """
    func = "core_course_get_contents"
    data = {
        "courseid": course_id
    }

    response = send_query(func, data, 200)
    return response


def get_attempt(attempt_id):
    """
    Get the information of a course.

    The parameters are defined and used to get the course information.
    Then, call the function send_query() with the parameters. It handles the actual request to Moodle.
    :param attempt_id: The attempt ID.
    :type attempt_id: str
    :return: All the information of the course in JSON.
    :rtype: json
    """
    func = 'mod_quiz_get_attempt_review'
    data = {
        "attemptid": attempt_id
    }

    response = send_query(func, data, 200)
    return response


def get_teachers(course_ids):
    """
    Get all the teachers for courses in Moodle.

    :param course_ids: List of course_id.
    :type course_ids: list(str)
    :return: All teachers.
    :rtype: dict
    """
    data = \
        {"coursecapabilities": [{
            "courseid": course_id,
            "capabilities":
                ["moodle/course:changefullname"]
        } for course_id in course_ids]}

    func = "core_enrol_get_enrolled_users_with_capability"
    response = send_query(func, data, 200)
    return response


def send_query(func, data, exp_status_code):
    """
    Send a query to Moodle in a certain format.

    :param exp_status_code: The expected status code a function should return on success.
    :type exp_status_code: int
    :param func: The web service function that is send to the api.
    :type func: str
    :param data: The parameters send for the function.
    :type data: dict
    :return: The Moodle response.
    :rtype: json
    """
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': TOKEN
    }
    response = requests.post(f'{URL}/{func}', headers=headers, json=data)
    if response.status_code != exp_status_code:
        logger.log_response(URL, status_code=response.status_code, headers=headers, text=response.text)
        print('Query failed, Response: ' + str(response.json()))
        raise MoodleException(f'Moodle error: {response.status_code}')

    return response.json()
