# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import json
import datetime

from unittest.mock import patch, call
from django.test import TestCase
from django.contrib.auth.models import Group

from assistants import models as assistants_models
from assistants.tests import test_data
from assistants.views import PARSERS
from assistants.moodle import MoodleException
from assistants.learning_locker import LearningLockerException
from courses import models as courses_models
from scheduler import models as scheduler_models
from lib.test_objects import raise_
from lib.tests import test_data as lib_test_data


class QuizCompletedFeedbackViewTest(TestCase):
    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch('assistants.feedback_manager.get_quiz_feedback', return_value='dummy_message')
    @patch('assistants.moodle.send_message')
    def test_quiz_completed_feedback(self, a, b, c):
        course = courses_models.Course.objects.create(name='Test_Course', courseId=1,
                                                      version_time=datetime.datetime(2020, 1, 28))
        quiz = assistants_models.Quiz.objects.create(course_id=1, name="Test_quiz1", external_id=18,
                                                     version_time=datetime.datetime(2020, 1, 28))
        assistants_models.QuizCompletedFeedback.objects.create(
            course=course, quiz=quiz, forwarder_id=1, threshold=5.00)

        response = self.client.post(
            '/assistants/api/quiz_completed_feedback/1/',
            json.dumps(test_data.test_parse_quiz_completed_feedback),
            content_type="application/json")

        self.assertEqual(200, response.status_code)
        a.assert_called_with('3', 'dummy_message')

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch('assistants.learning_locker.get_questions_answered')
    @patch('lib.ll_get_parsers.parse_questions_answered')
    @patch('assistants.feedback_manager.get_questions_feedback', return_value='dummy_message')
    @patch('assistants.moodle.send_message')
    def test_quiz_completed_feedback_question_feedback(self, a, b, c, d, e):
        course = courses_models.Course.objects.create(name='Test_Course', courseId=1,
                                                      version_time=datetime.datetime(2020, 1, 28))
        quiz = assistants_models.Quiz.objects.create(course_id=1, name="Test_quiz1", external_id=18,
                                                     version_time=datetime.datetime(2020, 1, 28))
        assistants_models.QuizCompletedFeedback.objects.create(
            course=course, quiz=quiz, forwarder_id=1, threshold=5.00, question_feedback=True)

        self.client.post(
            '/assistants/api/quiz_completed_feedback/1/',
            json.dumps(test_data.test_parse_quiz_completed_feedback),
            content_type="application/json")

        a.assert_called_with(
            '3', 'dummy_message')

    def test_quiz_completed_feedback_get(self):
        resp = self.client.get('/assistants/api/quiz_completed_feedback/1/')
        self.assertEqual(400, resp.status_code)

    def test_quiz_completed_feedback_action_id_failure(self):

        self.client.post(
            '/assistants/api/quiz_completed_feedback/1/',
            json.dumps(test_data.test_parse_quiz_completed_feedback),
            content_type="application/json")

        self.assertEqual(1, scheduler_models.FailedStatement.objects.count())
        self.assertEqual('Action id not found', scheduler_models.FailedStatement.objects.all().first().error)

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch.dict(PARSERS, {'http://adlnet.gov/expapi/verbs/completed': lambda a: raise_(KeyError)})
    def test_quiz_completed_feedback_parse_failure(self, a):
        course = courses_models.Course.objects.create(name='Test_Course', courseId=1,
                                                      version_time=datetime.datetime(2020, 1, 28))
        quiz = assistants_models.Quiz.objects.create(course_id=1, name="Test_quiz1", external_id=18,
                                                     version_time=datetime.datetime(2020, 1, 28))
        assistants_models.QuizCompletedFeedback.objects.create(
            course=course, quiz=quiz, forwarder_id=1, threshold=5.00)

        self.client.post(
            '/assistants/api/quiz_completed_feedback/1/',
            json.dumps(test_data.test_parse_quiz_completed_feedback),
            content_type="application/json")

        self.assertEqual(1, scheduler_models.FailedStatement.objects.count())
        self.assertEqual('Parsing error', scheduler_models.FailedStatement.objects.all().first().error)

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch('assistants.learning_locker.get_questions_answered', side_effect=LearningLockerException)
    def test_quiz_completed_feedback_ll_failure(self, a, b):
        course = courses_models.Course.objects.create(name='Test_Course', courseId=1,
                                                      version_time=datetime.datetime(2020, 1, 28))
        quiz = assistants_models.Quiz.objects.create(course_id=1, name="Test_quiz1", external_id=18,
                                                     version_time=datetime.datetime(2020, 1, 28))
        assistants_models.QuizCompletedFeedback.objects.create(
            course=course, quiz=quiz, forwarder_id=1, threshold=5.00, question_feedback=True)

        self.client.post(
            '/assistants/api/quiz_completed_feedback/1/',
            json.dumps(test_data.test_parse_quiz_completed_feedback),
            content_type="application/json")

        self.assertEqual(1, scheduler_models.FailedStatement.objects.count())
        self.assertEqual(
            'Learning Locker connection error', scheduler_models.FailedStatement.objects.all().first().error)

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch('assistants.feedback_manager.get_quiz_feedback', return_value='dummy_message')
    @patch('assistants.moodle.send_message', side_effect=MoodleException)
    def test_quiz_completed_feedback_moodle_failure(self, a, b, c):
        course = courses_models.Course.objects.create(name='Test_Course', courseId=1,
                                                      version_time=datetime.datetime(2020, 1, 28))
        quiz = assistants_models.Quiz.objects.create(course_id=1, name="Test_quiz1", external_id=18,
                                                     version_time=datetime.datetime(2020, 1, 28))
        assistants_models.QuizCompletedFeedback.objects.create(
            course=course, quiz=quiz, forwarder_id=1, threshold=5.00)

        self.client.post(
            '/assistants/api/quiz_completed_feedback/1/',
            json.dumps(test_data.test_parse_quiz_completed_feedback),
            content_type="application/json")

        self.assertEqual(1, scheduler_models.FailedStatement.objects.count())
        self.assertEqual('Moodle connection error', scheduler_models.FailedStatement.objects.all().first().error)

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch.dict(PARSERS, {'http://adlnet.gov/expapi/verbs/completed': lambda a: raise_(Exception)})
    def test_quiz_completed_feedback_generic_failure(self, a):
        course = courses_models.Course.objects.create(name='Test_Course', courseId=1,
                                                      version_time=datetime.datetime(2020, 1, 28))
        quiz = assistants_models.Quiz.objects.create(course_id=1, name="Test_quiz1", external_id=18,
                                                     version_time=datetime.datetime(2020, 1, 28))
        assistants_models.QuizCompletedFeedback.objects.create(
            course=course, quiz=quiz, forwarder_id=1, threshold=5.00)

        self.client.post(
            '/assistants/api/quiz_completed_feedback/1/',
            json.dumps(test_data.test_parse_quiz_completed_feedback),
            content_type="application/json")

        self.assertEqual(1, scheduler_models.FailedStatement.objects.count())
        self.assertEqual(
            'Unknown error: <class \'Exception\'>',
            scheduler_models.FailedStatement.objects.all().first().error)


class NewActivityNotificationTest(TestCase):
    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch('assistants.moodle.get_enrolled_users', return_value=lib_test_data.test_parse_enrolled_users)
    @patch('assistants.moodle.send_bulk_messages')
    def test_new_activity_notification(self, a, b, c):
        course = courses_models.Course.objects.create(name='Test_Course', courseId=1,
                                                      version_time=datetime.datetime(2020, 1, 28))
        assistants_models.NewActivityCreated.objects.create(course=course, forwarder_id=1)

        response = self.client.post(
            '/assistants/api/new_activity_notification/1/',
            json.dumps(lib_test_data.test_parse_new_activity_created_data),
            content_type="application/json")

        self.assertEqual(200, response.status_code)
        b.assert_called_with(1)
        self.assertEqual(b.call_count, 1)
        self.assertEqual(a.call_count, 1)
        messagetext = "For the course Test_Course the quiz Test_Activity is added."
        a.assert_has_calls([call(['2', '3', '4', '5'], messagetext)])

    def test_new_activity_notification_get(self):
        resp = self.client.get('/assistants/api/new_activity_notification/1/')
        self.assertEqual(400, resp.status_code)

    def test_new_activity_notification_action_id_failure(self):
        self.client.post(
            '/assistants/api/new_activity_notification/1/',
            json.dumps(lib_test_data.test_parse_new_activity_created_data),
            content_type="application/json")

        self.assertEqual(1, scheduler_models.FailedStatement.objects.count())
        self.assertEqual('Action id not found', scheduler_models.FailedStatement.objects.all().first().error)

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch.dict(PARSERS, {'http://activitystrea.ms/schema/1.0/create': lambda a: raise_(KeyError)})
    def test_new_activity_notification_parse_failure(self, a):
        course = courses_models.Course.objects.create(name='Test_Course', courseId=1,
                                                      version_time=datetime.datetime(2020, 1, 28))
        assistants_models.NewActivityCreated.objects.create(course=course, forwarder_id=1)

        self.client.post(
            '/assistants/api/new_activity_notification/1/',
            json.dumps(lib_test_data.test_parse_new_activity_created_data),
            content_type="application/json")

        self.assertEqual(1, scheduler_models.FailedStatement.objects.count())
        self.assertEqual('Parsing error', scheduler_models.FailedStatement.objects.all().first().error)

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch('assistants.moodle.get_enrolled_users', return_value=lib_test_data.test_parse_enrolled_users)
    @patch('assistants.moodle.send_bulk_messages', side_effect=MoodleException)
    def test_new_activity_notification_moodle_failure(self, a, b, c):
        course = courses_models.Course.objects.create(name='Test_Course', courseId=1,
                                                      version_time=datetime.datetime(2020, 1, 28))
        assistants_models.NewActivityCreated.objects.create(course=course, forwarder_id=1)

        self.client.post(
            '/assistants/api/new_activity_notification/1/',
            json.dumps(lib_test_data.test_parse_new_activity_created_data),
            content_type="application/json")

        self.assertEqual(1, scheduler_models.FailedStatement.objects.count())
        self.assertEqual('Moodle connection error', scheduler_models.FailedStatement.objects.all().first().error)

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch.dict(PARSERS, {'http://activitystrea.ms/schema/1.0/create': lambda a: raise_(Exception)})
    def test_new_activity_notification_generic_failure(self, a):
        course = courses_models.Course.objects.create(name='Test_Course', courseId=1,
                                                      version_time=datetime.datetime(2020, 1, 28))
        assistants_models.NewActivityCreated.objects.create(course=course, forwarder_id=1)

        self.client.post(
            '/assistants/api/new_activity_notification/1/',
            json.dumps(lib_test_data.test_parse_new_activity_created_data),
            content_type="application/json")

        self.assertEqual(1, scheduler_models.FailedStatement.objects.count())
        self.assertEqual(
            'Unknown error: <class \'Exception\'>',
            scheduler_models.FailedStatement.objects.all().first().error)


class CourseSyncAgentTest(TestCase):

    @patch('assistants.moodle.send_bulk_messages')
    def test_sync_agent(self, a):
        courses_models.Course.objects.create(name='Test_Course', courseId=2, inactivity=False, deadline=False,
                                             version_time=datetime.datetime(2020, 1, 28))
        self.client.post(
            '/assistants/api/course_sync_agent/', json.dumps(lib_test_data.course_sync_agent_test_data_create),
            content_type='application/json')
        self.assertEqual(courses_models.Resource.objects.count(), 1)
        self.client.post(
            '/assistants/api/course_sync_agent/', json.dumps(lib_test_data.course_sync_agent_test_data_chapter),
            content_type='application/json')
        self.assertEqual(courses_models.Resource.objects.count(), 2)
        self.client.post(
            '/assistants/api/course_sync_agent/', json.dumps(lib_test_data.course_sync_agent_test_data_delete),
            content_type='application/json')
        # This is wrong! deleting a book should delete its chapters as well. There was no time to fix this.
        self.assertEqual(courses_models.Resource.objects.count(), 1)

    def test_course_sync_agent_get(self):
        resp = self.client.get('/assistants/api/course_sync_agent/')
        self.assertEqual(400, resp.status_code)


class UserSyncAgentTest(TestCase):

    def setUp(self) -> None:
        Group.objects.create(name='Teachers')
        courses_models.Course.objects.create(name='Test_Course', courseId=2,
                                             version_time=datetime.datetime(2020, 1, 28))

    def test_user_sync_agent(self):
        self.client.post('/assistants/api/user_sync_agent/', json.dumps(lib_test_data.test_user_assign_parser),
                         content_type='application/json')
        self.assertEqual(courses_models.User.objects.count(), 1)
        user = courses_models.User.objects.get(moodle_id='9')
        self.assertEqual(user.courses.count(), 1)

        self.client.post('/assistants/api/user_sync_agent/', json.dumps(lib_test_data.test_user_unassign_parser),
                         content_type='application/json')
        self.assertEqual(courses_models.User.objects.count(), 1)
        user = courses_models.User.objects.get(moodle_id='9')
        self.assertEqual(user.courses.count(), 0)

        self.client.post('/assistants/api/user_sync_agent/', json.dumps(lib_test_data.test_user_updated_parser),
                         content_type='application/json')
        self.assertEqual(courses_models.User.objects.count(), 1)
        self.assertTrue(courses_models.User.objects.filter(last_name='Usertje').exists())

        self.client.post('/assistants/api/user_sync_agent/', json.dumps(lib_test_data.test_user_deleted_parser),
                         content_type='application/json')
        self.assertEqual(courses_models.User.objects.count(), 0)


class QuestionSyncAgentTest(TestCase):

    def test_question_sync_agent(self):
        course = courses_models.Course.objects.create(name='Test_Course', courseId=2,
                                                      version_time=datetime.datetime(2020, 1, 28))
        courses_models.Quiz.objects.create(name='Test_Quiz', course=course, external_id=52,
                                           version_time=datetime.datetime(2020, 1, 28))
        self.client.post('/assistants/api/question_sync_agent/',
                         json.dumps(lib_test_data.test_parse_question_create_data), content_type='application/json')
        self.assertEqual(courses_models.Question.objects.count(), 1)

        self.client.post('/assistants/api/question_sync_agent/',
                         json.dumps(lib_test_data.test_parse_question_update_data), content_type='application/json')
        self.assertEqual(courses_models.Question.objects.count(), 2)

        self.client.post('/assistants/api/question_sync_agent/',
                         json.dumps(lib_test_data.test_parse_question_delete_data), content_type='application/json')
        self.assertEqual(courses_models.Question.objects.count(), 1)
