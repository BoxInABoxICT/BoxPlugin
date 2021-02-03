# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""This file contains all communication from and to Learning Locker."""
import json
import requests
import time
import sys
from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import assistants.learning_locker as ll_api
import assistants.models as a_models
import courses.models as c_models
from scheduler.models import FailedStatement, ProcessedStatement, IGNORED_VERBS
from scheduler.main_scheduler import main_scheduler


def cron_job():
    """Run the error handling cron job."""
    now = time.time()
    validate_statements(e_handler.last_operation)
    e_handler.last_operation = now
    execute_statements_from_db()


def validate_statements(since, until=None, activity=None, verb=None):
    """
    Validate statements using the known-statements database. Unprocessed statements are added to the Failedstatements.

    :param since: String that returns statements stored after the given timestamp (exclusive).
    :param until: String that returns statements stored before the given timestamp (inclusive). Defaults to None.
    :param activity: String matching the statement’s object identifier. Defaults to None.
    :param verb: String matching the statement’s verb identifier. Defaults to None.
    """
    parameters = {'since': since}

    if until is not None:
        parameters['until'] = until
    if activity is not None:
        parameters['activity'] = activity
    if verb is not None:
        parameters['verb'] = verb

    statements = ll_api.get_statements(parameters)

    for statement in reversed(statements['statements']):
        statement_id = statement['id']
        statement_verb = statement['verb']['id']
        statement_type = statement['object']['definition']['type']

        _, created = ProcessedStatement.objects.get_or_create(statement_id=statement_id)

        # Edit_page_viewed event is allowed
        if (created and (statement_verb not in IGNORED_VERBS or statement_type == 'http://activitystrea.ms/schema/1.0/page')):
            FailedStatement.objects.create(
                statement=json.dumps(statement), error='Unforwarded statement')


def quiz_completed(statement):
    """
    Get link for a user update.

    :param statement: the xAPI statement
    :return: The url location.
    """
    quiz_id = int(statement['object']['id'].split("id=")[1])
    quiz = c_models.Quiz.objects.get(external_id=quiz_id)
    agent_id = a_models.QuizCompletedFeedback.objects.get(quiz=quiz).id
    return f'/assistants/api/new_activity_notification/{agent_id}/'


def course_change(statement):
    """
    Get link for a user update.

    :param statement: the xAPI statement
    :return: The url location.
    """
    s_verb = statement['verb']['id']
    if s_verb != 'http://activitystrea.ms/schema/1.0/create':
        course_id = int(statement['object']['id'].split("id=")[1])
        course = c_models.Course.objects.get(courseId=course_id)
        s_time = statement['timestamp'].split('+')[0]
        if datetime.strptime(s_time, '%Y-%m-%dT%H:%M:%S') < course.version_time:
            raise ValueError()
    return '/assistants/api/course_sync_agent/'


def chapter_change(statement):
    """
    Get link for a user update.

    :param statement: the xAPI statement
    :return: The url location.
    """
    s_verb = statement['verb']['id']
    if s_verb != 'http://activitystrea.ms/schema/1.0/create':
        course_id = int(statement['context']['contextActivities']['grouping'][1]['id'].split('=')[-1])
        course = c_models.Course.objects.get(courseId=course_id)
        module_id = int(statement['object']['id'].split('=')[-1])
        module = c_models.Resource.objects.get(course=course, external_id=module_id)
        s_time = statement['timestamp'].split('+')[0]
        if datetime.strptime(s_time, '%Y-%m-%dT%H:%M:%S') < module.version_time:
            raise ValueError()
    return '/assistants/api/course_sync_agent/'


def module_change(statement, link):
    """
    Get link for a user update.

    :param statement: the xAPI statement
    :param link: the mofa url
    :return: The url location.
    """
    s_verb = statement['verb']['id']
    if s_verb != 'http://activitystrea.ms/schema/1.0/create':
        course_id = int(statement['context']['contextActivities']['grouping'][1]['id'].split('=')[-1])
        course = c_models.Course.objects.get(courseId=course_id)
        object_target = \
            urlparse(statement['object']['id'])._replace(netloc=urlparse(settings.MOODLE_BASE_URL).netloc).geturl()
        object_id = int(object_target.split('=')[-1])
        object_type = urlparse(object_target).path.split('/')[2]

        if object_type == 'assign':
            module = c_models.Assignment.objects.get(course=course, external_id=object_id)
        elif object_type == 'quiz':
            module = c_models.Quiz.objects.get(course=course, external_id=object_id)
        elif object_type == 'choice':
            module = c_models.Choice.objects.get(course=course, external_id=object_id)
        else:
            module = c_models.Resource.objects.get(course=course, external_id=object_id)

        s_time = statement['timestamp'].split('+')[0]
        if datetime.strptime(s_time, '%Y-%m-%dT%H:%M:%S') < module.version_time:
            raise ValueError()

        try:
            agent_id = a_models.NewActivityCreated.objects.get(course=course).id
            resp = requests.post(
                f'{link}/assistants/api/new_activity_notification/{agent_id}/',
                headers={'Content-Type': 'application/json'},
                json={'statement': statement})
            if resp.status_code != 200:
                raise ConnectionError()
        except ObjectDoesNotExist:
            pass

    return '/assistants/api/course_sync_agent/'


def user_change(statement):
    """
    Get link for a user update.

    :param statement: the xAPI statement
    :return: The url location.
    """
    s_verb = statement['verb']['id']
    if s_verb != 'http://activitystrea.ms/schema/1.0/create':
        user_id = statement['object']['id'].split('=')[-1]
        user = c_models.User.objects.get(moodle_id=user_id)
        s_time = statement['timestamp'].split('+')[0]
        if datetime.strptime(s_time, '%Y-%m-%dT%H:%M:%S') < user.version_time:
            raise ValueError()
    return '/assistants/api/user_sync_agent/'


def role_change(statement):
    """
    Get link for a role update.

    :param statement: the xAPI statement
    :return: The url location.
    """
    return '/assistants/api/user_sync_agent/'


def quiz_question_change(statement):
    """
    Get link for a quiz question update.

    :param statement: the xAPI statement
    :return: The url location.
    """
    return '/assistants/api/question_sync_agent/'


def execute_statement(statement):
    """
    Send a statement to the correct view.

    :param statement: contains the xAPI statement
    """
    try:
        s_type = statement['object']['definition']['type']
        link = f'http://localhost:{settings.DJANGO_PORT}'

        if s_type == 'http://adlnet.gov/expapi/activities/assessment':
            link += quiz_completed(statement)
        elif s_type == 'http://id.tincanapi.com/activitytype/lms/course':
            link += course_change(statement)
        elif s_type == 'http://id.tincanapi.com/activitytype/chapter':
            link += chapter_change(statement)
        elif s_type == 'http://id.tincanapi.com/activitytype/lms/module':
            link += module_change(statement, link)
        elif s_type == 'http://id.tincanapi.com/activitytype/user':
            link += user_change(statement)
        elif s_type.startswith('http://id.tincanapi.com/activitytype/role/'):
            link += role_change(statement)
        elif s_type == 'http://activitystrea.ms/schema/1.0/page':
            link += quiz_question_change(statement)
        else:
            raise LookupError()

        resp = requests.post(
            link,
            headers={'Content-Type': 'application/json'},
            json={'statement': statement})

        if resp.status_code != 200:
            raise ConnectionError()

    except KeyError:
        FailedStatement.objects.create(
            statement=json.dumps(statement), error='Parsing error')
    except ObjectDoesNotExist:
        FailedStatement.objects.create(
            statement=json.dumps(statement), error='Missing assistant or Course item')
    except ValueError:
        return
    except LookupError:
        FailedStatement.objects.create(
            statement=json.dumps(statement), error='Unknown type')
    except ConnectionError:
        FailedStatement.objects.create(
            statement=json.dumps(statement), error=f'Mofa connection failure')
    except Exception:
        FailedStatement.objects.create(
            statement=json.dumps(statement), error=f'Unexpected error: {sys.exc_info()[0]}')


def execute_statements_from_db():
    """Reprocess failed statements."""
    statements = FailedStatement.objects.all()
    for fs in statements:
        json_fs = json.loads(fs.statement)
        execute_statement(json_fs)
        FailedStatement.objects.filter(pk=fs.id).delete()


def start_error_handling():
    """Start the error handling cron job to run every hour."""
    job = main_scheduler.scheduler.add_job(cron_job, 'interval', seconds=108000)
    main_scheduler.jobs["error handling"] = job


class ErrorHandler:
    """Stores the last operation datetime."""

    def __init__(self):
        """Initialize the error handler."""
        self.last_operation = time.time()


e_handler = ErrorHandler()
