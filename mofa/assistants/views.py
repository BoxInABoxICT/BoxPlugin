# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Views are created here."""
import json
import sys

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

import lib.ll_event_parsers
import lib.moodle_get_parsers
import lib.ll_get_parsers
from scheduler.models import FailedStatement
from assistants import feedback_manager, learning_locker, models, moodle
import assistants.sync_agent as sync_agent
import scheduler.error_handling as e_handling


@csrf_exempt
def quiz_completed_feedback(request, action_id):
    """
    Obtain statement forwards from LRS.

    :param request: HttpRequest representing the current request. Not being used.
    :type request: WSGIRequest
    :param action_id: The id of a action.
    :type action_id: int
    :return: HTTP response.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        try:
            msg_sent = False
            request_json = json.loads(request.body)
            action = models.QuizCompletedFeedback.objects.get(id=action_id)
            api = DESTINATIONS[action.course.platform]
            params = PARSERS[action.event](request_json)
            if action.question_feedback:
                questions_json = learning_locker.get_questions_answered(params['attempt_id'], params['quiz_id'])
                questions = lib.ll_get_parsers.parse_questions_answered(questions_json)
                question_message = feedback_manager.get_questions_feedback(params, questions)
                if not question_message == '':
                    api.send_message(params['actor_id'], question_message)
                    msg_sent = True
            if not msg_sent:
                quiz_message = feedback_manager.get_quiz_feedback(params, action)
                if not quiz_message == '':
                    api.send_message(params['actor_id'], quiz_message)

        except models.QuizCompletedFeedback.DoesNotExist:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Action id not found')
        except KeyError:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Parsing error')
        except learning_locker.LearningLockerException:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Learning Locker connection error')
        except moodle.MoodleException:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Moodle connection error')
        except Exception:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error=f'Unknown error: {sys.exc_info()[0]}')

        return HttpResponse('POST request: Assistant successfully run')
    return HttpResponseBadRequest('Invalid data')


@csrf_exempt
def new_activity_notification(request, action_id):
    """
    Obtain statement forwards from LRS when "created" is called.

    When created is for a course, do nothing. When it is for a module (activity) send a message about the new
    activity to all the enrolled users of that course.
    :param request: HttpRequest representing the current request. Not being used.
    :type request: WSGIRequest
    :param action_id: The id of a action.
    :type action_id: int
    :return: HTTP response.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        try:
            request_json = json.loads(request.body)
            action = models.NewActivityCreated.objects.get(id=action_id)
            object_id = request_json['statement']['object']['id']
            # Check if it is an assignment/quiz that is being created. If not do nothing.
            if "quiz" in object_id or "assign" in object_id:
                params = PARSERS[action.event](request_json)
                message = models.build_new_activity_notification(
                    params['course_name'], params['activity_name'], params['activity_type'])
                api = DESTINATIONS[action.course.platform]
                students_in_JSON = api.get_enrolled_users(params['courseId'])
                student_ids = lib.moodle_get_parsers.parse_enrolled_students(students_in_JSON)
                # Send all students that are enrolled in the course the message about the new activity.
                api.send_bulk_messages(student_ids, message)

        except models.NewActivityCreated.DoesNotExist:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Action id not found')
        except KeyError:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Parsing error')
        except moodle.MoodleException:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Moodle connection error')
        except Exception:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error=f'Unknown error: {sys.exc_info()[0]}')

        return HttpResponse('POST request: Assistant successfully run')
    return HttpResponseBadRequest('Invalid data')


@csrf_exempt
def course_sync_agent_execute(request):
    """
    Execute update of database when a course changes.

    :param request: HttpRequest representing the current request. Not being used.
    :type request: WSGIRequest
    :return: HTTP response.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        try:
            request_json = json.loads(request.body)
            is_course = lib.ll_event_parsers.check_course_sync_agent_type(request_json)
            if is_course:
                parsed_json = lib.ll_event_parsers.parse_course_sync_agent_data(request_json)
                COURSE_DATABASE_ACTIONS[parsed_json['verb']](parsed_json)
            else:
                parsed_json = lib.ll_event_parsers.parse_module_sync_agent_data(request_json)
                MODULE_DATABASE_ACTIONS[parsed_json['verb']](parsed_json)

        except KeyError:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Parsing error')
        except ObjectDoesNotExist:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Module does not exist')
        except moodle.MoodleException:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Moodle connection error')
        except Exception:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error=f'Unknown error: {sys.exc_info()[0]}')

        return HttpResponse('POST request: Database successfully updated')
    return HttpResponseBadRequest('Invalid data')


@csrf_exempt
def user_sync_agent_execute(request):
    """
    Execute update of the database when a user changes.

    :param request: Contains the request information of learning locker.
    :type request: WSGIRequest
    :return: HTTP response.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        try:
            request_json = json.loads(request.body)
            verb = lib.ll_event_parsers.check_user_sync_agent_type(request_json)
            if verb == 'assigned':
                parsed_json = lib.ll_event_parsers.parse_user_assign_sync_agent_data(request_json)
                sync_agent.user_assigned(parsed_json)
            elif verb == 'unassigned':
                parsed_json = lib.ll_event_parsers.parse_user_unassign_sync_agent_data(request_json)
                sync_agent.user_unassigned(parsed_json)
            elif verb == 'deleted':
                parsed_json = lib.ll_event_parsers.parse_user_delete_sync_agent_data(request_json)
                sync_agent.user_deleted(parsed_json)
            else:
                parsed_json = lib.ll_event_parsers.parse_user_update_sync_agent_data(request_json)
                sync_agent.user_updated(parsed_json)

        except KeyError:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Parsing error')
        except ObjectDoesNotExist:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Course does not exist')
        except Exception:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error=f'Unknown error: {sys.exc_info()[0]}')

        return HttpResponse('POST request: Database successfully updated')
    return HttpResponseBadRequest('Invalid data')


@csrf_exempt
def question_sync_agent_execute(request):
    """
    Execute update of the database when a question changes.

    :param request: contains the request information of learning locker.
    :type request: WSGIRequest
    :return: HTTP response.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        try:
            request_json = json.loads(request.body)
            if lib.ll_event_parsers.check_question_update_data(request_json):
                parsed_json = lib.ll_event_parsers.parse_question_update_sync_agent_data(request_json)
                sync_agent.question_update_create(parsed_json)

        except KeyError:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Parsing error')
        except ObjectDoesNotExist:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error='Course/quiz/question link does not exist')
        except Exception:
            FailedStatement.objects.create(
                statement=json.dumps(request_json['statement']), error=f'Unknown error: {sys.exc_info()[0]}')

        return HttpResponse('POST request: Database successfully updated')
    return HttpResponseBadRequest('Invalid data')


e_handling.start_error_handling()

DESTINATIONS = {
    'Moodle': moodle
}

PARSERS = {
    'http://activitystrea.ms/schema/1.0/create': lib.ll_event_parsers.parse_new_activity_created,
    'http://adlnet.gov/expapi/verbs/completed': lib.ll_event_parsers.parse_quiz_completed_feedback,
}

MODULE_DATABASE_ACTIONS = {
    'created': sync_agent.module_update_or_create,
    'updated': sync_agent.module_update_or_create,
    'deleted': sync_agent.module_delete,
}

COURSE_DATABASE_ACTIONS = {
    'created': sync_agent.course_update_or_create,
    'updated': sync_agent.course_update_or_create,
    'deleted': sync_agent.course_delete,
}
