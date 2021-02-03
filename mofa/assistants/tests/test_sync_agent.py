# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import datetime
from django.test import TestCase
from unittest.mock import patch
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group

import assistants.sync_agent as db_update
import assistants.tests.test_data as test_data
from courses.models import Course, Resource, Quiz, Question, Assignment, Choice, User, Role


class TestDatabaseUpdateCourse(TestCase):

    def setUp(self) -> None:
        """Set up of test."""
        Course.objects.create(name='test-course', courseId=2,
                              version_time=datetime.datetime(2020, 1, 28))

    @patch('assistants.moodle.send_bulk_messages')
    def test_create_update_delete_content(self, a):
        db_update.module_update_or_create(test_data.test_database_create_resource)
        self.assertEqual(1, Resource.objects.count())
        db_update.module_update_or_create(test_data.test_database_update_resource)
        self.assertEqual(1, Resource.objects.count())
        self.assertEqual('Advanced', Resource.objects.first().name)
        db_update.module_delete(test_data.test_database_update_resource)
        self.assertEqual(0, Resource.objects.count())

    @patch('assistants.moodle.send_bulk_messages')
    def test_create_update_delete_assignment(self, a):
        db_update.module_update_or_create(test_data.test_database_create_assign)
        self.assertEqual(1, Assignment.objects.count())
        db_update.module_update_or_create(test_data.test_database_update_assign)
        self.assertEqual(1, Assignment.objects.count())
        self.assertEqual('For Loops', Assignment.objects.first().name)
        db_update.module_delete(test_data.test_database_update_assign)
        self.assertEqual(0, Assignment.objects.count())

    @patch('assistants.moodle.send_bulk_messages')
    def test_create_update_delete_quiz(self, a):
        db_update.module_update_or_create(test_data.test_database_create_quiz)
        self.assertEqual(1, Quiz.objects.count())
        db_update.module_update_or_create(test_data.test_database_update_quiz)
        self.assertEqual(1, Quiz.objects.count())
        self.assertEqual('For', Quiz.objects.first().name)
        db_update.module_delete(test_data.test_database_update_quiz)
        self.assertEqual(0, Quiz.objects.count())

    @patch('assistants.moodle.send_bulk_messages')
    def test_create_update_delete_choice(self, a):
        db_update.module_update_or_create(test_data.test_database_create_choice)
        self.assertEqual(1, Choice.objects.count())
        db_update.module_update_or_create(test_data.test_database_update_choice)
        self.assertEqual(1, Choice.objects.count())
        self.assertEqual('F', Choice.objects.first().name)
        db_update.module_delete(test_data.test_database_update_choice)
        self.assertEqual(0, Choice.objects.count())

    @patch('assistants.moodle.send_bulk_messages')
    def test_create_update_delete_course(self, a):
        db_update.course_update_or_create(test_data.test_database_create_course)
        self.assertEqual(2, Course.objects.count())
        db_update.course_update_or_create(test_data.test_database_update_course)
        self.assertEqual(2, Course.objects.count())
        self.assertEqual('Python', Course.objects.last().name)
        db_update.course_delete(test_data.test_database_update_course)
        self.assertEqual(1, Course.objects.count())

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    def test_create_sync_agent(self, a):
        db_update.create_course_sync_agent()

        a.assert_called_with('course_sync_agent',
                             query='{\n  "$and": [\n    {\n      "$comment": "{\\"criterionLabel\\":\\"A\\",\\"criteri'
                             'aPath\\":[\\"statement\\",\\"verb\\"]}",\n      "statement.verb.id": {\n        "$in": ['
                             '\n          "http://activitystrea.ms/schema/1.0/create",\n          "http://activitystre'
                             'a.ms/schema/1.0/update",\n          "http://activitystrea.ms/schema/1.0/delete"\n       '
                             ' ]\n      }\n    },\n    {\n      "statement.object.definition.type": {\n        "$nin":'
                             ' [\n          "http://id.tincanapi.com/activitytype/user"\n        ]\n      }\n    }\n '
                             ' ]\n}')

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch('assistants.learning_locker.get_sync_agent_forwarder',
           return_value=test_data.test_build_sync_agent_get_data_empty)
    def test_build_sync_agent(self, a, b):
        db_update.build_sync_agents()

        b.assert_called_with('question_sync_agent',
                             query='{\n  "$and": [\n    {\n      "$comment": "{\\"criterionLabel\\":\\"A\\",\\"criter'
                                   'iaPath\\":[\\"statement\\",\\"verb\\"]}",\n      "statement.verb.id": {\n        '
                                   '"$in": [\n          "http://id.tincanapi.com/verb/viewed"\n        ]\n      }\n  '
                                   '  },\n    {\n      "$comment": "{\\"criterionLabel\\":\\"B\\",\\"criteriaPath\\":['
                                   '\\"statement\\",\\"object\\",\\"definition\\",\\"type\\"]}",\n      "statement.obj'
                                   'ect.definition.type": {\n        "$in": [\n          "http://activitystrea.ms/sche'
                                   'ma/1.0/page"\n        ]\n      }\n    }\n  ]\n}')

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch('assistants.learning_locker.get_sync_agent_forwarder',
           return_value=test_data.test_build_sync_agent_get_data)
    def test_dont_build_sync_agent(self, a, b):
        db_update.build_sync_agents()

        self.assertFalse(b.called)

    def test_no_course_with_course_id(self):
        Course.objects.all().delete()
        with self.assertRaises(ObjectDoesNotExist):
            db_update.module_update_or_create(test_data.test_database_create_assign)


class TestDatabaseUpdateUserAssign(TestCase):

    def setUp(self) -> None:
        Group.objects.create(name='Teachers')
        Course.objects.create(name='test-course', courseId=2,
                              version_time=datetime.datetime(2020, 1, 28))
        user = User(username='test_user', first_name='Test', last_name='User', email='test@test.nl',
                    moodle_id=3, is_staff=True, version_time=datetime.datetime(2020, 1, 28))
        user.set_password('Test123!')
        user.save()
        group = Group.objects.get(name='Teachers')
        user.groups.add(group)

    def test_assigned_course_user(self):
        db_update.user_assigned(test_data.test_database_assign_user)
        self.assertEqual(1, User.objects.count())
        user2 = User.objects.get(moodle_id=test_data.test_database_assign_user['id'])
        self.assertEqual('test_user', user2.username)
        self.assertTrue(user2.courses.filter(courseId=2).exists())

    def test_assigned_course_no_user(self):
        User.objects.all().delete()
        db_update.user_assigned(test_data.test_database_assign_user)
        self.assertEqual(1, User.objects.count())
        user = User.objects.get(moodle_id=test_data.test_database_assign_user['id'])
        self.assertEqual('test_user', user.username)

    def test_assigned_no_course_user(self):
        Course.objects.all().delete()
        with self.assertRaises(ObjectDoesNotExist):
            db_update.user_assigned(test_data.test_database_assign_user)
        self.tearDown()


class TestDatabaseUpdateUserUnassign(TestCase):

    def setUp(self) -> None:
        Group.objects.create(name='Teachers')

    def test_unassigned_user_course(self):
        course = Course.objects.create(name='test-course', courseId=2,
                                       version_time=datetime.datetime(2020, 1, 28))
        user = User(username='test_user', first_name='Test', last_name='User', email='test@test.nl',
                    moodle_id=3, is_staff=True, version_time=datetime.datetime(2020, 1, 28))
        user.set_password('Test123!')
        user.save()
        group = Group.objects.get(name='Teachers')
        user.groups.add(group)
        Role.objects.create(user_id=user, course_id=course, role_type='editingteacher')
        db_update.user_unassigned(test_data.test_database_unassign_user)
        self.assertEqual(0, user.courses.count())

    def test_updated_user(self):
        db_update.user_updated(test_data.test_database_updated_user)
        self.assertTrue(User.objects.filter(last_name='Usertje').exists)

    def test_deleted_user(self):
        db_update.user_deleted(test_data.test_database_deleted_user)
        self.assertEqual(0, User.objects.count())

    def test_updated_no_user(self):
        db_update.user_updated(test_data.test_database_updated_user)
        self.assertEqual(0, User.objects.count())


class TestDatabaseUpdateQuestion(TestCase):

    def test_question_create(self):
        course = Course.objects.create(name='Test_Course', courseId=2, version_time=datetime.datetime(2020, 1, 28))
        Quiz.objects.create(course=course, name='Test_Quiz', external_id=52,
                            version_time=datetime.datetime(2020, 1, 28))
        db_update.question_update_create(test_data.test_question_create)
        self.assertEqual(1, Quiz.objects.count())
        self.assertEqual(1, Question.objects.count())

        db_update.question_update_create(test_data.test_question_update)
        self.assertEqual(1, Quiz.objects.count())
        self.assertEqual(2, Question.objects.count())

        db_update.question_update_create(test_data.test_question_delete)
        self.assertEqual(1, Quiz.objects.count())
        self.assertEqual(0, Question.objects.count())
