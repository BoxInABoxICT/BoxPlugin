# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Django management commands for courses app."""

from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand
from django.utils import timezone

from assistants import moodle, learning_locker
from assistants.moodle import get_teachers
from courses.models import Course, User, Role, Resource, Quiz, Assignment, Choice, Question
from lib import moodle_get_parsers, ll_get_parsers
from lib.moodle_get_parsers import parse_get_teachers
from django.conf import settings

PERMISSION_LIST = [
    "add_quizcompletedfeedback",
    "change_quizcompletedfeedback",
    "delete_quizcompletedfeedback",
    "view_quizcompletedfeedback",
    "add_newactivitycreated",
    "change_newactivitycreated",
    "delete_newactivitycreated",
    "view_newactivitycreated",
    "add_resource",
    "change_resource",
    "delete_resource",
    "view_resource",
    "change_course",
    "view_course",
    "add_subject",
    "change_subject",
    "delete_subject",
    "view_subject",
    "change_quiz",
    "view_quiz",
    "change_question",
    "view_question",
    "change_choice",
    "view_choice",
    "change_assignment",
    "view_assignment"
]


class Command(BaseCommand):
    """Remove all data from Mofa and imports all courses and teachers from Moodle."""

    help = 'Removes course data and gets the latest course data from Moodle'

    def handle(self, *args, **options):
        """Define main method."""
        self.stdout.write("Be careful, this command will delete everything in Mofa!")

        yes = {'yes', 'y'}
        no = {'no', 'n', ''}

        choice = input("Do you want to proceed? [y/N]:").lower()
        if choice in yes:
            for course in Course.objects.all():
                if not course.delete():
                    self.stdout.write("The statement forwarder of an assistant was not present in Learning Locker. "
                                      "The assistant will still be deleted.")

            for teacher in User.objects.filter(is_superuser=False):
                self.stdout.write(f"Deleted teacher {teacher.first_name} {teacher.last_name}")
                teacher.delete()

            Group.objects.all().delete()

            import_courses()
            import_course_content()
            teacher_count = import_teachers()
            self.stdout.write('Hooray, Moodle successfully imported')
            self.stdout.write('{} course(s) are loaded from Moodle'.format(Course.objects.count()))
            self.stdout.write('{} assignment(s) are loaded from Moodle'.format(Assignment.objects.count()))
            self.stdout.write('{} quiz(zes) are loaded from Moodle'.format(Quiz.objects.count()))
            self.stdout.write('{} question(s) are loaded from Moodle'.format(Question.objects.count()))
            self.stdout.write('{} choice(s) are loaded from Moodle'.format(Choice.objects.count()))
            self.stdout.write('{} resource item(s) are loaded from Moodle'.format(Resource.objects.count()))
            self.stdout.write('{} teacher(s) are loaded from Moodle'.format(teacher_count))
            return

        if choice in no:
            return

        else:
            print('\nYour input was not recognised, please try again.')
            self.handle()


def import_courses():
    """Import courses from Moodle and add to Django database."""
    courses = moodle_get_parsers.parse_courses(moodle.get_courses())
    Course.objects.bulk_create(Course(**params, version_time=timezone.now()) for params in courses)


def import_course_content():
    """Import course content from Moodle and add to Django database."""
    course_list = dict(Course.objects.values_list("courseId", "pk"))
    courses_contents = get_course_contents_for_all_courses(course_list)
    grouped_dict = group_course_contents(courses_contents)
    question_list = get_quiz_questions(grouped_dict)
    fill_database(grouped_dict, question_list)


def get_course_contents_for_all_courses(course_list):
    """
    Get all course contents from Moodle for all courses.

    :param course_list: List of dictionary. Key: external course id. Value: mofa course id.
    :type course_list: dict(str, int)
    :return: List of dictionaries of course contents for all the courses in course_list.
    :rtype: list(dict(str, int)
    """
    courses_contents = []
    for course in course_list.keys():
        courses_contents.extend(
            moodle_get_parsers.parse_get_course_contents(
                moodle.get_course_contents(course), course_list[course])
        )
    return courses_contents


def group_course_contents(courses_contents):
    """
    Group all the course contents by content type.

    :param courses_contents: List of dictionaries of course contents for all the courses in course_list.
    :type courses_contents: list(dict(str, int)
    :return: A dictionary with a list of each of the assessments and resources.
    :rtype: dict(str, list(dict(str, int)))
    """
    grouped_dict = {}
    for content in courses_contents:
        if content['type'] in grouped_dict:
            grouped_dict[content['type']].append(content)
        else:
            grouped_dict[content['type']] = [content]

    return grouped_dict


def get_quiz_questions(grouped_dict):
    """
    Get the quiz questions for all quizzes individually and combine them.

    :param grouped_dict: A dictionary with a list of each of the assessments and resources.
    :type grouped_dict: dict(str,list(dict(str, int)))
    :return: A dictionary with questions.
    :rtype: dict(int, list(dict(str, str)))
    """
    if 'quiz' not in grouped_dict:
        return []

    question_list = {}
    quiz_ids = [quiz['external_id'] for quiz in grouped_dict['quiz']]
    for quiz_id in quiz_ids:
        params = {
            "verb": "http://id.tincanapi.com/verb/viewed",
            "activity": f"{settings.MOODLE_BASE_URL}/mod/quiz/edit.php?cmid={quiz_id}",
            "limit": 1
        }

        questions = ll_get_parsers.parse_quiz_questions(learning_locker.get_statements(params))

        if quiz_id in questions:
            question_list[quiz_id] = questions[quiz_id]
        else:
            question_list[quiz_id] = []

    return question_list


def fill_database(grouped_dict, question_list):
    """
    Fill the database with all specified course contents.

    :param grouped_dict: A dictionary with a list of each of the assessments and resources.
    :type grouped_dict: dict(str,list(dict(str, int)))
    :param question_list: A dictionary with questions.
    :type question_list: dict(int, list(dict(str, str)))
    """
    for content_type, content in grouped_dict.items():
        if content_type == 'assign':
            Assignment.objects.bulk_create([Assignment(course_id=a['course_id'], name=a['name'],
                                                       external_id=a['external_id'],
                                                       version_time=timezone.now()) for a in content])
        elif content_type == 'quiz':
            Quiz.objects.bulk_create([Quiz(course_id=a['course_id'], name=a['name'],
                                           external_id=a['external_id'],
                                           version_time=timezone.now()) for a in content])
        elif content_type == 'choice':
            Choice.objects.bulk_create([Choice(course_id=a['course_id'], name=a['name'],
                                               external_id=a['external_id'],
                                               version_time=timezone.now()) for a in content])
        else:
            Resource.objects.bulk_create([Resource(external=False,
                                                   version_time=timezone.now(), **a) for a in content])

    quiz_list = dict(Quiz.objects.values_list("external_id", "pk"))
    for quiz_id in question_list:
        course = Quiz.objects.get(pk=quiz_list[quiz_id]).course
        Question.objects.bulk_create([Question(name=a['question_name'], external_id=a['question_id'],
                                               quiz_id=quiz_list[quiz_id], course=course,
                                               version_time=timezone.now())
                                      for a in question_list[quiz_id]])


def import_teachers():
    """
    Import the teachers from Moodle.

    :return: Amount of imported users.
    :rtype: int
    """
    course_list = dict(Course.objects.values_list("courseId", "pk"))
    teachers_list = parse_get_teachers(get_teachers(list(course_list.keys())))
    teacher_group = create_auth_group()
    users = create_teachers(teachers_list)
    add_courses_and_group_to_users(course_list, teacher_group, teachers_list, users)
    return users.count()


def create_auth_group():
    """
    Create teacher group, add permissions add to Django database.

    :return: Teacher auth group.
    :rtype Auth Group
    """
    teacher_group = Group.objects.create(name='Teachers')
    for permission_name in PERMISSION_LIST:
        permission = Permission.objects.get(codename=permission_name)
        teacher_group.permissions.add(permission)
    return teacher_group


def create_teachers(teachers_list):
    """
    Create teachers and add them to Django database.

    :param teachers_list: Dictionary of teachers.
    :type teachers_list: dict(int, dict(str, str))
    :return: A QuerySet of teachers.
    :rtype: QuerySet

    """
    user_list = []
    for teacher in teachers_list.values():
        user = User(username=teacher['username'], moodle_id=teacher['id'], email=teacher['email'],
                    first_name=teacher['firstname'], last_name=teacher['lastname'], is_staff=True,
                    version_time=timezone.now())

        user.set_password("Test123!")
        user_list.append(user)
    User.objects.bulk_create(user_list)
    users = User.objects.all()
    return users


def add_courses_and_group_to_users(course_list, teacher_group, teachers_list, users):
    """
    Add courses the teacher teaches to that teacher. Add teacher to teachers group.

    :param course_list: List of courses.
    :type course_list: dict(int, int)
    :param teacher_group: Teachers group.
    :type teacher_group: Auth Group
    :param teachers_list: Dictionary of teachers.
    :type teachers_list: dict(int, dict(str, str))
    :param users: QuerySet of all the teachers.
    :type users: QuerySet
    """
    for user in users:
        if user.moodle_id in teachers_list:
            course_ids = [course_list[course] for course in teachers_list[user.moodle_id]['courses'].keys()]
            for i_d in course_ids:
                course = Course.objects.get(pk=i_d)
                for role in teachers_list[user.moodle_id]['courses'][course.courseId]:
                    Role.objects.create(user_id=user, course_id=course, role_type=role)
            user.groups.add(teacher_group)
