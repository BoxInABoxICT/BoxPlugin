# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import datetime
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.db.models import Count
from django.test import TestCase

from courses.management.commands.import_moodle import create_auth_group, create_teachers, \
    add_courses_and_group_to_users
from courses.management.commands.import_moodle import fill_database, group_course_contents, Command, get_quiz_questions
from courses.models import Assignment, Course, Choice, Resource, Quiz, Question
from courses.models import User
from courses.tests import test_data
from lib.tests.test_data import test_parse_get_course_contents, test_parse_get_courses, \
    test_parse_quiz_question_data, test_parse_quiz_question


class TestImportMoodle(TestCase):
    # patch on assistants.moodle.get_teachers did not work so patch on assistants.moodle.send_query
    @patch('builtins.input', return_value="yes")
    @patch('assistants.moodle.get_courses', return_value=test_parse_get_courses)
    @patch('assistants.moodle.get_course_contents', return_value=test_parse_get_course_contents)
    @patch('assistants.learning_locker.get_statements', return_value=test_parse_quiz_question)
    @patch('assistants.moodle.send_query', return_value=test_data.test_parse_get_teachers)
    def test_handle(self, a, b, c, d, e):
        command = Command()
        command.handle()

        self.assertEqual(Course.objects.count(), 3)
        self.assertEqual(c.call_count, 3)
        self.assertEqual(Assignment.objects.count(), 6)
        self.assertEqual(Quiz.objects.count(), 3)
        self.assertEqual(Question.objects.count(), 2)
        self.assertEqual(Choice.objects.count(), 6)
        self.assertEqual(Resource.objects.count(), 33)
        self.assertEqual(User.objects.all().count(), 2)
        self.assertEqual(Group.objects.all().count(), 1)
        self.assertEqual(User.objects.annotate(group_count=Count('groups')).count(), 2)

    def test_create_auth_group(self):
        self.assertEqual(create_auth_group().permissions.count(), 26)

    def test_create_teachers(self):
        create_teachers(test_data.test_teachers_list)
        self.assertEqual(User.objects.all().count(), 2)

    def test_add_courses_and_group_to_users(self):
        User.objects.bulk_create([
            User(username='tom', moodle_id=3, email='tom@gmail.com', first_name='Tom', last_name='Tree',
                 is_staff=True, version_time=datetime.datetime(2020, 1, 28)),
            User(username='sam', moodle_id=5, email='sam@gmail.com', first_name='Sam',
                 last_name='Smith', is_staff=True, version_time=datetime.datetime(2020, 1, 28))
        ])
        course_list = {2: 1, 4: 2}
        Group.objects.create(name='Teachers')
        users = User.objects.all()
        add_courses_and_group_to_users(course_list, Group.objects.get(name='Teachers'),
                                       test_data.test_parse_get_teachers, users)
        self.assertEqual(User.objects.annotate(group_count=Count('groups')).count(), 2)

    def test_fill_database(self):
        Course.objects.bulk_create([Course(pk=159, name="Testing course", courseId=1,
                                           version_time=datetime.datetime(2020, 1, 28)),
                                    Course(pk=161, name="Testing course", courseId=2,
                                           version_time=datetime.datetime(2020, 1, 28))])
        fill_database(test_data.test_grouped_dict, test_parse_quiz_question_data)

        self.assertEqual(Assignment.objects.count(), 3)
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Choice.objects.count(), 3)
        self.assertEqual(Resource.objects.count(), 13)
        self.assertEqual(Question.objects.count(), 2)

    def test_group_course_contents(self):
        self.assertEqual(group_course_contents(test_data.test_group_contents), test_data.test_grouped_dict)

    @patch('assistants.learning_locker.get_statements', return_value=test_parse_quiz_question)
    def test_get_quiz_questions(self, a):
        self.assertEqual(get_quiz_questions(test_data.test_grouped_dict), test_parse_quiz_question_data)
