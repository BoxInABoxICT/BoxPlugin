# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

import json
import datetime
from django.test import TestCase
from unittest.mock import patch, call
from django.core.exceptions import ObjectDoesNotExist

from lib.test_objects import MockResponse, STATEMENTS
from scheduler.models import FailedStatement, ProcessedStatement
import courses.models as courses_models
import assistants.models as assistants_models
import scheduler.error_handling as eh_api


class TestErrorHandlingAPI(TestCase):
    @patch('scheduler.error_handling.validate_statements')
    @patch('scheduler.error_handling.execute_statements_from_db')
    @patch('time.time', return_value=1.1)
    def test_cron_job(self, a, b, c):
        eh_api.e_handler.last_operation = 0.0

        eh_api.cron_job()

        c.assert_called_with(0.0)

        self.assertEqual(1.1, eh_api.e_handler.last_operation)

    @patch('assistants.learning_locker.get_statements')
    def test_validate_statements_all(self, a):
        eh_api.validate_statements(
            'dummy_time_1', until='dummy_time_2',
            activity='dummy_activity', verb='dummy_verb')

        a.assert_called_with(
            {
                'since': 'dummy_time_1',
                'until': 'dummy_time_2',
                'activity': 'dummy_activity',
                'verb': 'dummy_verb'
            })

    @patch('assistants.learning_locker.get_statements', return_value={'statements': [STATEMENTS[0], STATEMENTS[1]]})
    def test_validate_statements_2_for_2(self, a):
        ProcessedStatement(statement_id='dummy-statement-id-2').save()
        ProcessedStatement(statement_id='dummy-statement-id-1').save()

        eh_api.validate_statements('dummy_time')

        self.assertEqual(0, FailedStatement.objects.count())

    @patch('assistants.learning_locker.get_statements', return_value={'statements': [STATEMENTS[0]]})
    def test_validate_statements_1_for_2(self, a):
        ProcessedStatement(statement_id='dummy-statement-id-1').save()
        ProcessedStatement(statement_id='dummy-statement-id-2').save()

        eh_api.validate_statements('dummy_time')

        self.assertEqual(0, FailedStatement.objects.count())

    @patch('assistants.learning_locker.get_statements', return_value={'statements': [STATEMENTS[0], STATEMENTS[1]]})
    def test_validate_statements_2_for_1(self, a):
        ProcessedStatement(statement_id='dummy-statement-id-1').save()

        eh_api.validate_statements('dummy_time')

        self.assertEqual(1, FailedStatement.objects.count())
        self.assertTrue(FailedStatement.objects.filter(statement=json.dumps(STATEMENTS[1])).exists())

    @patch('assistants.learning_locker.get_statements', return_value={'statements': [STATEMENTS[2]]})
    def test_validate_statements_ignore_other_viewed(self, a):
        eh_api.validate_statements('dummy_time')

        self.assertEqual(0, FailedStatement.objects.count())

    def test_quiz_question_change_valid(self):
        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://activitystrea.ms/schema/1.0/update'
            },
            'object': {
                'definition': {
                    'type': 'http://activitystrea.ms/schema/1.0/page'
                }
            }
        }

        ret = eh_api.quiz_question_change(statement)

        self.assertEqual('/assistants/api/question_sync_agent/', ret)

    def test_quiz_question_change_invalid(self):
        pass

    def test_role_change_valid(self):
        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://activitystrea.ms/schema/1.0/assign'
            },
            'object': {
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/role/student'
                }
            }
        }

        ret = eh_api.role_change(statement)

        self.assertEqual('/assistants/api/user_sync_agent/', ret)

    def test_role_change_invalid(self):
        pass

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    def test_quiz_completed_valid(self, a):
        course = courses_models.Course.objects.create(name='Dummy_Course', courseId=1, version_time=datetime.datetime(2020, 1, 28))
        quiz = assistants_models.Quiz.objects.create(course_id=1,
                                                     name='Dummy_quiz', external_id=3,
                                                     version_time=datetime.datetime(2020, 1, 28))
        assistants_models.QuizCompletedFeedback.objects.create(
            course=course, quiz=quiz, forwarder_id=1, threshold=5.00)

        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://adlnet.gov/expapi/verbs/completed'
            },
            'object': {
                'id': 'http://localhost:4000/mod/quiz/view.php?id=3',
                'definition': {
                    'type': 'http://adlnet.gov/expapi/activities/assessment'
                }
            }
        }

        ret = eh_api.quiz_completed(statement)

        self.assertEqual('/assistants/api/new_activity_notification/1/', ret)

    def test_quiz_completed_invalid(self):
        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://adlnet.gov/expapi/verbs/completed'
            },
            'object': {
                'id': 'http://localhost:4000/mod/quiz/view.php?id=3',
                'definition': {
                    'type': 'http://adlnet.gov/expapi/activities/assessment'
                }
            }
        }

        with self.assertRaises(ObjectDoesNotExist):
            eh_api.quiz_completed(statement)

    def test_chapter_change_valid(self):
        course = courses_models.Course.objects.create(
            name='Course 0', courseId=1, version_time=datetime.datetime(2020, 1, 28))
        courses_models.Resource.objects.create(
            course=course, name='chapter 1', type='Book', target="site",
            external_id=8, version_time=datetime.datetime(2020, 1, 28))

        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://activitystrea.ms/schema/1.0/update'
            },
            'object': {
                "id": "http://localhost:8002/mod/book/view.php?id=1&chapterid=8",
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/chapter'
                }
            },
            "context": {
                "contextActivities": {
                    "grouping": [
                        {"id": "http://localhost:8002"},
                        {"id": "http://localhost:8002/course/view.php?id=1"}
                    ]
                }
            },
            "timestamp": "2020-01-30T18:50:32+00:00"
        }

        ret = eh_api.chapter_change(statement)

        self.assertEqual('/assistants/api/course_sync_agent/', ret)

    def test_chapter_change_invalid(self):
        course = courses_models.Course.objects.create(
            name='Course 0', courseId=1, version_time=datetime.datetime(2020, 1, 28))
        courses_models.Resource.objects.create(
            course=course, name='chapter 1', type='Book', target="site",
            external_id=8, version_time=datetime.datetime(2020, 1, 28))

        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://activitystrea.ms/schema/1.0/update'
            },
            'object': {
                "id": "http://localhost:8002/mod/book/view.php?id=1&chapterid=8",
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/chapter'
                }
            },
            "context": {
                "contextActivities": {
                    "grouping": [
                        {"id": "http://localhost:8002"},
                        {"id": "http://localhost:8002/course/view.php?id=1"}
                    ]
                }
            },
            "timestamp": "2020-01-20T18:50:32+00:00"
        }

        with self.assertRaises(ValueError):
            eh_api.chapter_change(statement)

    def test_user_change_valid(self):
        courses_models.User.objects.create(username='tom', moodle_id=3, email='tom@gmail.com',
                                           first_name='Tom', last_name='Tree', is_staff=True,
                                           version_time=datetime.datetime(2020, 1, 28))
        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://activitystrea.ms/schema/1.0/update'
            },
            'object': {
                'id': 'http://localhost:8002/user/profile.php?id=3',
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/user'
                }
            },
            "timestamp": "2020-01-30T18:50:32+00:00"
        }

        ret = eh_api.user_change(statement)

        self.assertEqual('/assistants/api/user_sync_agent/', ret)

    def test_user_change_invalid(self):
        courses_models.User.objects.create(username='tom', moodle_id=3, email='tom@gmail.com',
                                           first_name='Tom', last_name='Tree', is_staff=True,
                                           version_time=datetime.datetime(2020, 1, 28))
        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://activitystrea.ms/schema/1.0/update'
            },
            'object': {
                'id': 'http://localhost:8002/user/profile.php?id=3',
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/user'
                }
            },
            "timestamp": "2020-01-20T18:50:32+00:00"
        }

        with self.assertRaises(ValueError):
            eh_api.user_change(statement)

    def test_course_change_valid(self):
        courses_models.Course.objects.create(
            name='Course 0', courseId=1, version_time=datetime.datetime(2020, 1, 28))
        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://activitystrea.ms/schema/1.0/update'
            },
            'object': {
                'id': 'http://localhost:8002/course/view.php?id=1',
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/lms/course'
                }
            },
            "timestamp": "2020-01-30T18:50:32+00:00"
        }

        ret = eh_api.course_change(statement)

        self.assertEqual('/assistants/api/course_sync_agent/', ret)

    def test_course_change_invalid(self):
        courses_models.Course.objects.create(
            name='Course 0', courseId=1, version_time=datetime.datetime(2020, 1, 28))
        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://activitystrea.ms/schema/1.0/update'
            },
            'object': {
                'id': 'http://localhost:8002/course/view.php?id=1',
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/lms/course'
                }
            },
            "timestamp": "2020-01-20T18:50:32+00:00"
        }

        with self.assertRaises(ValueError):
            eh_api.course_change(statement)

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch('requests.post', return_value=MockResponse(200))
    def test_module_change_valid(self, a, b):
        course = courses_models.Course.objects.create(
            name='Course 0', courseId=1, version_time=datetime.datetime(2020, 1, 28))
        courses_models.Choice.objects.create(
            course=course, name='Dummy Choice', external_id=20,
            version_time=datetime.datetime(2020, 1, 28))
        assistants_models.NewActivityCreated.objects.create(course=course, forwarder_id=1)
        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://activitystrea.ms/schema/1.0/update'
            },
            'object': {
                'id': 'http://localhost:8002/mod/choice/view.php?id=20',
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/lms/module'
                }
            },
            "context": {
                "contextActivities": {
                    "grouping": [
                        {"id": "http://localhost:8002"},
                        {"id": "http://localhost:8002/course/view.php?id=1"}
                    ]
                }
            },
            "timestamp": "2020-01-30T18:50:32+00:00"
        }

        ret = eh_api.module_change(statement, 'http://localhost:1234')

        self.assertEqual('/assistants/api/course_sync_agent/', ret)

        a.assert_called_with(
            'http://localhost:1234/assistants/api/new_activity_notification/1/',
            headers={'Content-Type': 'application/json'},
            json={'statement': statement})

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch('requests.post', return_value=MockResponse(400))
    def test_module_change_invalid_mofa_access(self, a, b):
        course = courses_models.Course.objects.create(
            name='Course 0', courseId=1, version_time=datetime.datetime(2020, 1, 28))
        courses_models.Assignment.objects.create(
            course=course, name='Dummy Assignments', external_id=20,
            version_time=datetime.datetime(2020, 1, 28))
        assistants_models.NewActivityCreated.objects.create(course=course, forwarder_id=1)
        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://activitystrea.ms/schema/1.0/update'
            },
            'object': {
                'id': 'http://localhost:8002/mod/assign/view.php?id=20',
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/lms/module'
                }
            },
            "context": {
                "contextActivities": {
                    "grouping": [
                        {"id": "http://localhost:8002"},
                        {"id": "http://localhost:8002/course/view.php?id=1"}
                    ]
                }
            },
            "timestamp": "2020-01-30T18:50:32+00:00"
        }
        with self.assertRaises(ConnectionError):
            eh_api.module_change(statement, 'http://localhost:1234')

    @patch('assistants.learning_locker.create_statement_forwarder', return_value={'_id': 1})
    @patch('requests.post', return_value=MockResponse(400))
    def test_module_change_invalid_agent(self, a, b):
        course1 = courses_models.Course.objects.create(
            name='Course 0', courseId=1, version_time=datetime.datetime(2020, 1, 28))
        course2 = courses_models.Course.objects.create(
            name='Course other', courseId=2, version_time=datetime.datetime(2020, 1, 28))
        courses_models.Quiz.objects.create(
            course=course1, name='Dummy Assignments', external_id=20,
            version_time=datetime.datetime(2020, 1, 28))
        assistants_models.NewActivityCreated.objects.create(course=course2, forwarder_id=1)
        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://activitystrea.ms/schema/1.0/update'
            },
            'object': {
                'id': 'http://localhost:8002/mod/quiz/view.php?id=20',
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/lms/module'
                }
            },
            "context": {
                "contextActivities": {
                    "grouping": [
                        {"id": "http://localhost:8002"},
                        {"id": "http://localhost:8002/course/view.php?id=1"}
                    ]
                }
            },
            "timestamp": "2020-01-30T18:50:32+00:00"
        }

        ret = eh_api.module_change(statement, 'http://localhost:1234')

        self.assertEqual('/assistants/api/course_sync_agent/', ret)

    def test_course_change_invalid_version_time(self):
        course = courses_models.Course.objects.create(
            name='Course 0', courseId=1, version_time=datetime.datetime(2020, 1, 28))
        courses_models.Resource.objects.create(
            course=course, name='chapter 1', type='Book', target="site",
            external_id=8, version_time=datetime.datetime(2020, 1, 28)
        )
        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://activitystrea.ms/schema/1.0/update'
            },
            'object': {
                'id': 'http://localhost:8002/mod/book/view.php?id=8',
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/lms/module'
                }
            },
            "context": {
                "contextActivities": {
                    "grouping": [
                        {"id": "http://localhost:8002"},
                        {"id": "http://localhost:8002/course/view.php?id=1"}
                    ]
                }
            },
            "timestamp": "2020-01-20T18:50:32+00:00"
        }

        with self.assertRaises(ValueError):
            eh_api.module_change(statement, 'http://localhost:1234')

    @patch('scheduler.error_handling.quiz_completed', return_value='/assistants/api/new_activity_notification/1')
    @patch('requests.post', return_value=MockResponse(200))
    def test_execute_statement_quiz_completed(self, a, b):
        statement = {
            'id': 'dummy-statement-id',
            'verb': {
                'id': 'http://adlnet.gov/expapi/verbs/completed'
            },
            'object': {
                'id': 'http://localhost:4000/mod/quiz/view.php?id=3',
                'definition': {
                    'type': 'http://adlnet.gov/expapi/activities/assessment'
                }
            }
        }

        eh_api.execute_statement(statement)

        a.assert_called_with(
            'http://localhost:1234/assistants/api/new_activity_notification/1',
            headers={'Content-Type': 'application/json'},
            json={'statement': statement})

    @patch('scheduler.error_handling.user_change', return_value='/assistants/api/user_sync_agent/')
    @patch('requests.post', return_value=MockResponse(200))
    def test_execute_statement_user_changed(self, a, b):
        statement = {
            'id': 'dummy-statement-id',
            'object': {
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/user'
                }
            }
        }

        eh_api.execute_statement(statement)

        a.assert_called_with(
            'http://localhost:1234/assistants/api/user_sync_agent/',
            headers={'Content-Type': 'application/json'},
            json={'statement': statement})

    @patch('scheduler.error_handling.role_change', return_value='/assistants/api/user_sync_agent/')
    @patch('requests.post', return_value=MockResponse(200))
    def test_execute_statement_role_changed(self, a, b):
        statement = {
            'id': 'dummy-statement-id',
            'object': {
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/role/teacher'
                }
            }
        }

        eh_api.execute_statement(statement)

        a.assert_called_with(
            'http://localhost:1234/assistants/api/user_sync_agent/',
            headers={'Content-Type': 'application/json'},
            json={'statement': statement})

    @patch('scheduler.error_handling.quiz_question_change', return_value='/assistants/api/question_sync_agent/')
    @patch('requests.post', return_value=MockResponse(400))
    def test_execute_statement_connection_error(self, a, b):
        statement = {
            'id': 'dummy-statement-id',
            'object': {
                'definition': {
                    'type': 'http://activitystrea.ms/schema/1.0/page'
                }
            }
        }

        eh_api.execute_statement(statement)

        self.assertEqual(1, FailedStatement.objects.count())
        self.assertEqual('Mofa connection failure', FailedStatement.objects.all().first().error)

    def test_execute_statement_unknown_type(self):
        statement = {
            'id': 'dummy-statement-id',
            'object': {
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/lms/unknown'
                }
            }
        }

        eh_api.execute_statement(statement)

        self.assertEqual(1, FailedStatement.objects.count())
        self.assertEqual('Unknown type', FailedStatement.objects.all().first().error)

    def test_execute_statement_parsing_error(self):
        statement = {}

        eh_api.execute_statement(statement)

        self.assertEqual(1, FailedStatement.objects.count())
        self.assertEqual('Parsing error', FailedStatement.objects.all().first().error)

    @patch('scheduler.error_handling.module_change', side_effect=ObjectDoesNotExist)
    def test_execute_statement_missing_assistant(self, a):
        statement = {
            'id': 'dummy-statement-id',
            'object': {
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/lms/module'
                }
            }
        }

        eh_api.execute_statement(statement)

        self.assertEqual(1, FailedStatement.objects.count())
        self.assertEqual('Missing assistant or Course item', FailedStatement.objects.all().first().error)

    @patch('scheduler.error_handling.chapter_change', side_effect=Exception)
    def test_execute_statement_unknown_error(self, a):
        statement = {
            'id': 'dummy-statement-id',
            'object': {
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/chapter'
                }
            }
        }

        eh_api.execute_statement(statement)

        self.assertEqual(1, FailedStatement.objects.count())
        self.assertEqual('Unexpected error: <class \'Exception\'>', FailedStatement.objects.all().first().error)

    @patch('scheduler.error_handling.course_change', side_effect=ValueError)
    @patch('requests.post', return_value=MockResponse(200))
    def test_execute_statement_value_error(self, a, b):
        statement = {
            'id': 'dummy-statement-id',
            'object': {
                'definition': {
                    'type': 'http://id.tincanapi.com/activitytype/lms/course'
                }
            }
        }

        eh_api.execute_statement(statement)

        self.assertEqual(0, FailedStatement.objects.count())
        a.assert_not_called()

    @patch('scheduler.error_handling.execute_statement')
    def test_execute_statement_from_db(self, a):
        statement_1 = {
            'id': 'dummy-statement-id-1',
            'verb': {
                'id': 'http://dummy-verb'
            }
        }
        statement_2 = {
            'id': 'dummy-statement-id-2',
            'verb': {
                'id': 'http://dummy-verb'
            }
        }
        FailedStatement(statement=json.dumps(statement_1), error='dummy-error').save()
        FailedStatement(statement=json.dumps(statement_2), error='dummy-error').save()

        eh_api.execute_statements_from_db()

        calls = [
            call({"id": "dummy-statement-id-1", "verb": {"id": "http://dummy-verb"}}),
            call({"id": "dummy-statement-id-2", "verb": {"id": "http://dummy-verb"}})]
        a.assert_has_calls(calls)
