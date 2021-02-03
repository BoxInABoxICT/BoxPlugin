# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""This file contains all communication from and to Learning Locker."""
import requests

from django.conf import settings
from . import logger

URL = settings.LL_URL
AUTH_KEY = settings.LL_AUTH_KEY
ORGANISATION = settings.ORGANISATION
CONNECT_ARGS = {
    'post': requests.post,
    'get': requests.get,
    'delete': requests.delete,
    'patch': requests.patch
}


class LearningLockerException(Exception):
    """Learning Locker exception."""

    pass


def connect(url, resp_code, method, headers=None, params=None, json=None):
    """
    Get all the statements matching the parameters.

    :param url: Url location on learning locker.
    :type url: str
    :param resp_code: Expected response value.
    :type resp_code: int
    :param method: information sending method.
    :type method: str
    :param headers: All additional for the request.
    :type headers: dict
    :param params: All parameters for the request.
    :type params: dict
    :param json: Json data. When added don't forget to add a header.
    :type json: dict
    :return: response data for Learning Locker.
    :rtype: Response
    """
    if headers is None:
        headers = {}
    headers['Authorization'] = f'Basic {AUTH_KEY}'
    if json is not None:
        headers['Content-Type'] = 'application/json'
    func = CONNECT_ARGS.get(method, LearningLockerException('Unknown HTTP request'))
    resp = func(f'{URL}{url}', params=params, headers=headers, json=json)

    if resp.status_code != resp_code:
        logger.log_response(URL, resp.status_code, params=params, headers=headers, json=json)
        raise LearningLockerException(f'Learning Locker Error: {resp.status_code}')

    return resp


def get_statements(parameters):
    """
    Get all the statements matching the parameters.

    :param parameters: All parameters for the request.
        Can be found on the learning locker get statements page.
    :type parameters: dict(str, str)
    :return: JSON data for Learning Locker.
    rtype: dict
    """
    header_data = {
        'X-Experience-API-Version': '1.0.3'
    }

    return connect(
        'data/xAPI/statements', 200, 'get',
        headers=header_data, params=parameters).json()


def get_viewed_courses(time, course_id):
    """
    Get all the viewed statements since a certain time.

    :param time: Get all the statements since this time.
    :type time: str
    :param course_id: ID of the course.
    :type course_id: str
    :return: JSON data for Learning Locker.
    :rtype: dict
    """
    parameters = {
        'verb': 'http://id.tincanapi.com/verb/viewed',
        'since': time,
        'activity': f'{settings.MOODLE_BASE_URL}/course/view.php?id={course_id}'
    }

    return get_statements(parameters)


def single_statement_deletion(s_id):
    """
    Delete a statement using its id.

    :param s_id: Statement ID (can be located on the LL platform).
    :type s_id: str
    """
    connect(f'api/v2/statement/{s_id}', 204, 'delete')


def batch_statement_deletion(filter_data):
    """
    Delete a batch using a filter.

    :param filter_data: The filter containing the keywords of statements
        that need to be removed. example: filter_data =
        'filter': {'statement.actor.name': 'Admin User',
        'statement.verb.display.en': 'viewed'}
    :type filter_data: dict(str, dict(str, str))
    """
    connect(f'api/v2/batchdelete/initialise', 200, 'post', json=filter_data)


def create_statement_forwarder(action, assistant_id=None, query='{}'):
    """
    Create a statement forwarder in Learning Locker.

    :param query: Contains query with what to forward.
    :type query: str
    :param action: The action the assistant will be performing e.g. Send Message.
    :type action: str
    :param assistant_id: The assistant id.
    :type assistant_id: str
    :return: Return the response JSON.
    :rtype: dict
    """
    if assistant_id:
        url = f'{settings.DJANGO_URL}:{settings.DJANGO_PORT}/assistants/api/{action}/{assistant_id}/'
        description = f'Statement Forwarder Assistant: {assistant_id}. Action: {action}'
    else:
        url = f'{settings.DJANGO_URL}:{settings.DJANGO_PORT}/assistants/api/{action}/'
        description = f'Statement Forwarder Agent: {action}'

    configuration = {
        'authType': 'no auth',
        'protocol': 'http',
        'url': url,
        'maxRetries': 10
    }
    json = {
        'query': query,
        'organisation': ORGANISATION,
        'active': 'true',
        'description': description,
        'fullDocument': 'true',
        'configuration': configuration
    }

    resp = connect('api/v2/statementforwarding', 201, 'post', json=json)

    return resp.json()


def delete_statement_forwarder(forwarder_id):
    """
    Delete a statement forwarder in Learning Locker.

    :param forwarder_id: The id of the statement forwarder.
    :type forwarder_id: str
    """
    connect(f'api/v2/statementforwarding/{forwarder_id}', 204, 'delete')


def update_statement_forwarder(forwarder_id, query=None, active=None, description=None, full_document=None):
    """
    Update a statement forwarder query in Learning Locker.

    :param forwarder_id: The id of the statement forwarder.
    :type forwarder_id: str
    :param query: The query that it should be updated with.
    :type query: str
    :param active: The active that it should be updated with.
    :type active: str
    :param description: The description that it should be updated with.
    :type description: str
    :param full_document: The full_document that it should be updated with.
    :type full_document: str
    :return: Return the request response
    :rtype: dict
    """
    json = {}
    if query is not None:
        json['query'] = query
    if active is not None:
        json['active'] = active
    if description is not None:
        json['description'] = description
    if full_document is not None:
        json['fullDocument'] = full_document

    resp = connect(f'api/v2/statementforwarding/{forwarder_id}', 200, 'patch', json=json)

    return resp.json()


def get_questions_answered(attempt_id, quiz_id):
    """
    Get all the questions answered from a certain attempt.

    :param attempt_id: Id of the attempt.
    :type attempt_id: str
    :param quiz_id: Id of the quiz.
    :type quiz_id: str
    :return: Dictionary of external (question_id: True/False) depending on the result of the question.
    :rtype: dict
    """
    params = {
        'filter': '{{"$and": [{{"relatedActivities": {{"$elemMatch":{{"$eq":"{u}/mod/quiz/attempt'
                  '.php?attempt={a}&cmid={q}"}}}}}},  {{"statement.verb.id":'
                  '"http://adlnet.gov/expapi/verbs/answered"}}]}}'.format(a=attempt_id, q=quiz_id,
                                                                          u=settings.MOODLE_BASE_URL)
    }

    resp = connect('api/connection/statement/', 200, 'get', params=params)
    json = resp.json()
    return json


def get_sync_agent_forwarder(agent_type):
    """
    Get the statement forwarder for the sync agent.

    :param agent_type: contains 'user' or 'course' depending on the type of sync agent.
    :type agent_type: str
    :return: The sync agent forwarder.
    :rtype: dict(list(dict(str, str)))
    """
    params = {
        'filter': '{{\"configuration.url\": \"{}\"}}'.format(f'{settings.SYNC_AGENT_URLS[agent_type]}')
    }

    resp = connect('api/connection/statementforwarding/', 200, 'get', params=params)
    return resp.json()


def check_statement_forwarder(forwarder_id):
    """
    Check if a statement forwarder is still in LL.

    :param forwarder_id: Id of the forwarder.
    :type forwarder_id: str
    :return: If the statement forwarder is in LL.
    :rtype: bool
    """
    try:
        connect(f'api/v2/statementforwarding/{forwarder_id}', 200, 'get')
    except LearningLockerException:
        return False
    else:
        return True


def get_all_statement_forwarders():
    """
    Get all statement forwarders from LL.

    :return: All statement forwarders.
    :type: json
    """
    resp = connect('api/v2/statementforwarding/', 200, 'get')
    return resp.json()
