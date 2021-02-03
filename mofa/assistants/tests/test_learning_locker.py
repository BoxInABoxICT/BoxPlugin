# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
from django.test import TestCase
from unittest.mock import MagicMock

from django.conf import settings
from lib.test_objects import MockResponse
import assistants.learning_locker as api


class TestLearningLockerAPI(TestCase):

    def setUp(self) -> None:
        get_mock = MagicMock()
        post_mock = MagicMock()
        patch_mock = MagicMock()
        delete_mock = MagicMock()

        api.CONNECT_ARGS = {
            'post': post_mock,
            'get': get_mock,
            'delete': patch_mock,
            'patch': delete_mock
        }

    def test_connect_unknown_http_request(self):
        with self.assertRaises(Exception):
            api.connect('data/xAPI/statements', 200, 'test')

    def test_get_statements_correct_status(self):
        api.CONNECT_ARGS['get'].return_value = MockResponse(200)
        api.get_statements({'dummy_time': 'dummy_value'})

        api.CONNECT_ARGS['get'].assert_called_with(
            'DUMMY_LL_URL/data/xAPI/statements',
            headers={'Authorization': 'Basic DUMMY_LL_AUTH_KEY', 'X-Experience-API-Version': '1.0.3'},
            params={'dummy_time': 'dummy_value'}, json=None)

    def test_get_statements_incorrect_status(self):
        api.CONNECT_ARGS['get'].return_value = MockResponse(400)
        with self.assertRaises(Exception):
            api.get_statements({'dummy_time': 'dummy_value'})

    def test_get_viewed_courses(self):
        api.CONNECT_ARGS['get'].return_value = MockResponse(200)
        api.get_viewed_courses('dummy_time', 'dummy_course_id')

        api.CONNECT_ARGS['get'].assert_called_with(
            'DUMMY_LL_URL/data/xAPI/statements',
            headers={'Authorization': 'Basic DUMMY_LL_AUTH_KEY', 'X-Experience-API-Version': '1.0.3'},
            params={'verb': 'http://id.tincanapi.com/verb/viewed', 'since': 'dummy_time',
                    'activity': f'{settings.MOODLE_BASE_URL}/course/view.php?id=dummy_course_id'},
            json=None)

    def test_single_statement_deletion_correct_status(self):
        api.CONNECT_ARGS['delete'].return_value = MockResponse(204)
        api.single_statement_deletion('dummy_statement_id')

        api.CONNECT_ARGS['delete'].assert_called_with(
            'DUMMY_LL_URL/api/v2/statement/dummy_statement_id',
            headers={'Authorization': 'Basic DUMMY_LL_AUTH_KEY'}, params=None, json=None)

    def test_single_statement_deletion_incorrect_status(self):
        api.CONNECT_ARGS['delete'].return_value = MockResponse(404)
        with self.assertRaises(Exception):
            api.single_statement_deletion('dummy_statement_id')

    def test_batch_statement_deletion_correct_status(self):
        filter_data = {'filter': {'example.name': 'example_name'}}
        api.CONNECT_ARGS['post'].return_value = MockResponse(200)
        api.batch_statement_deletion(filter_data)

        api.CONNECT_ARGS['post'].assert_called_with(
            'DUMMY_LL_URL/api/v2/batchdelete/initialise',
            headers={'Authorization': 'Basic DUMMY_LL_AUTH_KEY', 'Content-Type': 'application/json'},
            json=filter_data, params=None)

    def test_batch_statement_deletion_incorrect_status(self):
        filter_data = {'filter': {'example.name': 'example_name'}}
        api.CONNECT_ARGS['delete'].return_value = MockResponse(404)
        with self.assertRaises(Exception):
            api.batch_statement_deletion(filter_data)

    def test_create_statement_forwarder_correct_status(self):
        api.CONNECT_ARGS['post'].return_value = MockResponse(201)
        api.create_statement_forwarder('example_action', 'example_assistant_id')

        api.CONNECT_ARGS['post'].assert_called_with(
            'DUMMY_LL_URL/api/v2/statementforwarding',
            headers={'Authorization': 'Basic DUMMY_LL_AUTH_KEY', 'Content-Type': 'application/json'},
            json={
                'query': '{}',
                'organisation': 'DUMMY_ORGANISATION',
                'active': 'true',
                'description': 'Statement Forwarder Assistant: example_assistant_id. Action: example_action',
                'fullDocument': 'true',
                'configuration': {
                    'authType': 'no auth',
                    'protocol': 'http',
                    'url': f'{settings.DJANGO_URL}:{settings.DJANGO_PORT}'
                           f'/assistants/api/example_action/example_assistant_id/',
                    'maxRetries': 10
                }},
            params=None)

    def test_create_statement_forwarder_incorrect_status(self):
        api.CONNECT_ARGS['post'].return_value = MockResponse(404)
        with self.assertRaises(Exception):
            api.create_statement_forwarder('example_action', 'example_assistant_id')

    def test_delete_statement_forwarder_correct_status(self):
        api.CONNECT_ARGS['delete'].return_value = MockResponse(204)
        api.delete_statement_forwarder('example_statement_id')

    def test_delete_statement_forwarder_incorrect_status(self):
        api.CONNECT_ARGS['delete'].return_value = MockResponse(404)
        with self.assertRaises(Exception):
            api.delete_statement_forwarder('example_statement_id')

    def test_update_statement_forwarder_correct_status_all(self):
        api.CONNECT_ARGS['patch'].return_value = MockResponse(200)
        api.update_statement_forwarder(
            'example_statement_id', query='{}', active='true',
            description='example_description', full_document='true')

        api.CONNECT_ARGS['patch'].assert_called_with(
            'DUMMY_LL_URL/api/v2/statementforwarding/example_statement_id',
            headers={'Authorization': 'Basic DUMMY_LL_AUTH_KEY', 'Content-Type': 'application/json'},
            json={'query': '{}', 'active': 'true', 'description': 'example_description', 'fullDocument': 'true'},
            params=None)

    def test_update_statement_forwarder_correct_status_none(self):
        api.CONNECT_ARGS['patch'].return_value = MockResponse(200)
        api.update_statement_forwarder('example_statement_id')

        api.CONNECT_ARGS['patch'].assert_called_with(
            'DUMMY_LL_URL/api/v2/statementforwarding/example_statement_id',
            headers={'Authorization': 'Basic DUMMY_LL_AUTH_KEY', 'Content-Type': 'application/json'},
            json={},
            params=None)

    def test_update_statement_forwarder_incorrect_status(self):
        api.CONNECT_ARGS['patch'].return_value = MockResponse(404)
        with self.assertRaises(Exception):
            api.update_statement_forwarder('example_statement_id')
