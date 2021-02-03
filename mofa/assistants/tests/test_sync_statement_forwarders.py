# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import datetime
from django.test import TestCase
from unittest.mock import patch

from courses.models import Course, Quiz, Resource
from assistants.models import QuizCompletedFeedback
from . import test_data
import assistants.management.commands.sync_statement_forwarders as ssf


@patch('assistants.learning_locker.create_statement_forwarder')
def create_base_database(m1):
    m1.return_value = {'_id': '5e1849cc34e93b75adc6c92d'}
    course = Course.objects.create(name='Test Course', courseId=2,
                                   version_time=datetime.datetime(2020, 1, 28))
    resource = Resource.objects.create(course=course, name='Test Book', type='book', target='test target',
                                       version_time=datetime.datetime(2020, 1, 28))
    quiz = Quiz.objects.create(course=course, name='test_quiz', external_id=2, resources=resource,
                               version_time=datetime.datetime(2020, 1, 28))
    QuizCompletedFeedback.objects.create(course=course, quiz=quiz)
    return course, quiz


@patch('assistants.learning_locker.create_statement_forwarder')
def create_create_forwarder_database(m1):
    course, quiz = create_base_database()
    m1.return_value = {'_id': '5e1849cc34e93b75adc6c92e'}
    QuizCompletedFeedback.objects.create(course=course, quiz=quiz)


class TestSyncstatmentforwarders(TestCase):
    @patch('assistants.learning_locker.get_all_statement_forwarders')
    @patch('assistants.learning_locker.delete_statement_forwarder')
    @patch('assistants.learning_locker.update_statement_forwarder')
    def test_sync_no_action_needed(self, m1, m2, m3):
        create_base_database()
        m3.return_value = test_data.test_get_statement_forwarders
        ssf.Command().check_statement_forwarder_sync()
        self.assertFalse(m1.called)
        self.assertFalse(m2.called)
        m3.assert_called_with()

    @patch('assistants.learning_locker.get_all_statement_forwarders')
    @patch('assistants.learning_locker.delete_statement_forwarder')
    @patch('assistants.learning_locker.update_statement_forwarder')
    def test_sync_delete_statement(self, m1, m2, m3):
        m3.return_value = test_data.test_get_statement_forwarders_delete
        ssf.Command().check_statement_forwarder_sync()
        self.assertFalse(m1.called)
        self.assertTrue(m2.called)
        m3.assert_called_with()

    @patch('assistants.learning_locker.get_all_statement_forwarders')
    @patch('assistants.learning_locker.delete_statement_forwarder')
    @patch('assistants.learning_locker.update_statement_forwarder')
    def test_sync_create_statement(self, m1, m2, m3):
        create_create_forwarder_database()
        m3.return_value = test_data.test_get_statement_forwarders
        ssf.Command().check_statement_forwarder_sync()
        self.assertTrue(m1.called)
        self.assertFalse(m2.called)
        m3.assert_called_with()
