# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""File contains functions that update the resources and assignments in the database."""

from django.template import loader
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group
from django.utils import timezone

from courses.models import Course, User, Quiz, Role
import assistants.learning_locker as ll_api
import assistants.moodle as moodle_api
import lib.ll_get_parsers as ll_get
from assistants.logger import log_assistants


def module_update_or_create(module):
    """
    Create new resource or update resource of a certain course.

    :param module: Contains the necessary info of the new resource.
    :type module: dict(str,int)
    """
    try:
        course = Course.objects.get(courseId=module['courseId'])
    except ObjectDoesNotExist:
        log_assistants(f'The course object with id: {module["courseId"]} does not exist!', 'Sync Agent')
        raise ObjectDoesNotExist(f'The course object with id: {module["courseId"]} does not exist!')

    object_type = module['type']

    defaults = {'name': module['name'], 'course': course, 'version_time': timezone.now}
    kwargs = {'external_id': module['external_id'], 'defaults': defaults}

    if object_type == 'assign':
        _, created = course.assignment_set.update_or_create(**kwargs)
    elif object_type == 'quiz':
        _, created = course.quiz_set.update_or_create(**kwargs)
    elif object_type == 'choice':
        _, created = course.choice_set.update_or_create(**kwargs)
    else:
        kwargs.update({'target': module['target'], 'type': object_type, 'external': False})
        _, created = course.resource_set.update_or_create(**kwargs)


def module_delete(module):
    """
    Delete certain resource from a certain course.

    :param module: Contains the necessary info of the to be deleted course.
    :type module: dict
    """
    course = Course.objects.get(courseId=module['courseId'])
    object_type = module['type']
    try:
        kwargs = {'external_id': module['external_id']}
        if object_type == 'assign':
            assignment = course.assignment_set.get(**kwargs)
            name = assignment.name
            assignment.delete()
        elif object_type == 'quiz':
            quiz = course.quiz_set.get(**kwargs)
            name = quiz.name
            for agent in course.quizcompletedfeedback_set.filter(quiz=quiz):
                agent.delete()
            quiz.delete()
        elif object_type == 'choice':
            choice = course.choice_set.get(**kwargs)
            name = choice.name
            choice.delete()
        else:
            kwargs = {'target': module['target']}
            content = course.resource_set.get(**kwargs)
            name = content.name
            content.delete()
    except ObjectDoesNotExist:
        log_assistants('Sync agent tried to delete an object not present in the database.',
                       'Sync Agent')
        return


def course_update_or_create(course):
    """
    Create or update a course entry in the database.

    :param course: Contains all necessary info for a creation or an update.
    :type course: dict(str, str)
    """
    defaults = {'name': course['course_name'], 'version_time': timezone.now}
    kwargs = {'courseId': course['courseId'], 'platform': course['platform'], 'defaults': defaults}
    Course.objects.update_or_create(**kwargs)


def course_delete(course):
    """
    Delete a course entry in the database.

    :param course: contains all necessary info for a deletion.
    :type course: dict(str, str)
    """
    kwargs = {'courseId': course['courseId']}
    for course in Course.objects.filter(**kwargs):
        course.delete()


def user_assigned(user):
    """
    Check if a user is assigned the editteacher or manager role and if so, add them to the database.

    :param user: information about the user.
    :type user: dict(str, str)
    """
    if user['role'] == 'editingteacher' or user['role'] == 'manager':
        try:
            course = Course.objects.get(courseId=user['course_id'])
        except ObjectDoesNotExist:
            log_assistants('Course does not exist.', 'Sync_Agent')
            raise ObjectDoesNotExist('Course does not exist.')

        user_exists = User.objects.filter(moodle_id=user['id']).exists()
        if user_exists:
            userdb = User.objects.get(moodle_id=user['id'])
            if not userdb.role_set.filter(course_id=course, role_type=user['role']).exists():
                Role.objects.create(user_id=userdb, course_id=course, role_type=user['role'])
        else:
            userdb = User(username=user['username'], moodle_id=user['id'], email=user['email'],
                          first_name=user['firstname'],
                          last_name=user['lastname'], is_staff=True, version_time=timezone.now())
            userdb.set_password("Test123!")
            userdb.save()
            teacher_group = Group.objects.get(name='Teachers')
            userdb.groups.add(teacher_group)
            Role.objects.create(user_id=userdb, course_id=course, role_type=user['role'])


def user_unassigned(user):
    """
    Relieves a user from its privileges to edit the course in Mofa.

    :param user: information about the user to perform the database change with.
    :type user: dict(str, str)
    """
    if user['role'] == 'editingteacher' or user['role'] == 'manager':
        user_exists = User.objects.filter(moodle_id=user['user_id']).exists()
        if user_exists:
            userdb = User.objects.get(moodle_id=user['user_id'])
            if userdb.courses.filter(courseId=user['course_id']).exists():
                course = userdb.courses.get(courseId=user['course_id'])
                Role.objects.filter(course_id=course, user_id=userdb, role_type=user['role']).delete()


def user_deleted(user):
    """
    Delete a user from Mofa when it is deleted from the LMS.

    :param user: information about the user to perform the database change with.
    :type user: dict(str, str)
    """
    try:
        User.objects.get(moodle_id=user['user_id']).delete()
    except ObjectDoesNotExist:
        return


def user_updated(user):
    """
    Update a user from Mofa if it exists in the database.

    :param user: New information about the new user to perform the database change with.
    :type user: dict(str, str)
    """
    if User.objects.filter(moodle_id=user['id']).exists():
        kwargs = {'first_name': user['firstname'], 'last_name': user['lastname'], 'username': user['username'],
                  'email': user['email'], 'version_time': timezone.now()}
        User.objects.filter(moodle_id=user['id']).update(**kwargs)


def question_update_create(q_info):
    """
    Update or create a question from Moodle.

    :param q_info: Information about the question.
    :type q_info: dict(str, str)
    """
    try:
        course = Course.objects.get(courseId=q_info['course_id'])
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist('The course linked to the updated quiz is not present in the database.')

    try:
        quiz = Quiz.objects.get(external_id=q_info['quiz_id'])
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist('The quiz linked to the updated questions is not present in the database.')

    db_questions = quiz.question_set.all()
    statement_questions = q_info['questions']
    if len(db_questions) <= len(statement_questions):
        for s_question in statement_questions:
            defaults = {'name': s_question['question_name'], 'course': course,
                        'quiz': quiz, 'version_time': timezone.now()}
            kwargs = {'defaults': defaults, 'external_id': s_question['question_id']}
            quiz.question_set.update_or_create(**kwargs)
    else:
        s_id_list = []
        for s_question in statement_questions:
            s_id_list.append(int(s_question['question_id']))
        for db_question in db_questions:
            if db_question.external_id not in s_id_list:
                db_question.delete()


sync_agents = ['course', 'user', 'question']


def build_sync_agents():
    """Build a sync_agent based on if it already present in the database or not."""
    for agent in sync_agents:
        forwarder_id = ll_get.parse_sync_agent_forwarder_id(ll_api.get_sync_agent_forwarder(agent))
        if forwarder_id == 0:
            print(f'sync_agent for: {agent} will be created...')
            globals()[f'create_{agent}_sync_agent']()


def create_course_sync_agent():
    """Create a course sync agent."""
    context = {
        'create': 'http://activitystrea.ms/schema/1.0/create',
        'update': 'http://activitystrea.ms/schema/1.0/update',
        'delete': 'http://activitystrea.ms/schema/1.0/delete'

    }
    query = loader.render_to_string('assistants/course_sync_agent_query.json', context)
    ll_api.create_statement_forwarder('course_sync_agent', query=query)


def create_user_sync_agent():
    """Create a user sync agent."""
    context = {
        'assign': 'http://activitystrea.ms/schema/1.0/assign',
        'unassign': 'http://activitystrea.ms/schema/1.0/unassign',
        'update': 'http://activitystrea.ms/schema/1.0/update',
        'delete': 'http://activitystrea.ms/schema/1.0/delete',
        'user': 'http://id.tincanapi.com/activitytype/user'
    }
    query = loader.render_to_string('assistants/user_sync_agent_query.json', context)
    ll_api.create_statement_forwarder('user_sync_agent', query=query)


def create_question_sync_agent():
    """Create a question sync agent."""
    context = {
        'view': 'http://id.tincanapi.com/verb/viewed',
        'type': 'http://activitystrea.ms/schema/1.0/page'
    }
    query = loader.render_to_string('assistants/question_sync_agent_query.json', context)
    ll_api.create_statement_forwarder('question_sync_agent', query=query)


def send_update_notification(course, message):
    """
    Send a message to all admin users linked to the course.

    :param course: Course in which a module has changed.
    :type course: Course
    :param message: The message that has to be sent.
    :type message: str
    """
    user_list = []
    for user in course.user_set.all():
        user_list.append(user.moodle_id)
    if len(user_list) > 0:
        moodle_api.send_bulk_messages(user_list, message)
