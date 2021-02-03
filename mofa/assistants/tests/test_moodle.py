# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
from unittest.mock import patch

from django.test import TestCase

import assistants.moodle as moodle_api
from . import test_data
from lib.test_objects import MockResponse
from lib.tests import test_data as lib_test_data


class TestMoodleAPI(TestCase):
    @patch('requests.post', return_value=MockResponse(200, test_data.test_moodle_send_message_return))
    def test_send_message_correct(self, a):
        moodle_api.send_message(2, 'TestMessage')

        a.assert_called_with('DUMMY_MOODLE_URL/core_message_send_instant_messages',
                             headers={'Content-Type': 'application/json', 'Accept': 'application/json',
                                      'Authorization': 'DUMMY_MOODLE_TOKEN'},
                             json={'messages': [{'touserid': 2, 'text': 'TestMessage'}]})

    @patch('requests.post', return_value=MockResponse(400))
    def test_send_message_incorrect(self, a):
        with self.assertRaises(Exception):
            moodle_api.send_message('3', True)

    @patch('requests.post', return_value=MockResponse(200, test_data.test_moodle_send_message_return))
    def test_send_bulk_message_correct(self, a):
        moodle_api.send_bulk_messages([2, 4, 5], 'TestMessage')

        a.assert_called_with('DUMMY_MOODLE_URL/core_message_send_instant_messages',
                             headers={'Content-Type': 'application/json', 'Accept': 'application/json',
                                      'Authorization': 'DUMMY_MOODLE_TOKEN'},
                             json={'messages': [{'touserid': 2, 'text': 'TestMessage'},
                                                {'touserid': 4, 'text': 'TestMessage'},
                                                {'touserid': 5, 'text': 'TestMessage'}]})

    @patch('requests.post', return_value=MockResponse(400))
    def test_send_bulk_messages_incorrect(self, a):
        with self.assertRaises(Exception):
            moodle_api.send_bulk_messages(4, 'TestMessage')

    @patch('requests.post', return_value=MockResponse(200, test_data.test_moodle_send_message_return))
    def test_send_bulk_different_messages_correct(self, a):
        moodle_api.send_bulk_different_messages([(2, 'TestMessage1'), (3, 'TestMessage2'), (4, 'TestMessage4')])

        a.assert_called_with('DUMMY_MOODLE_URL/core_message_send_instant_messages',
                             headers={'Content-Type': 'application/json', 'Accept': 'application/json',
                                      'Authorization': 'DUMMY_MOODLE_TOKEN'},
                             json={'messages': [{'touserid': 2, 'text': 'TestMessage1'},
                                                {'touserid': 3, 'text': 'TestMessage2'},
                                                {'touserid': 4, 'text': 'TestMessage4'}]})

    @patch('requests.post', return_value=MockResponse(400))
    def test_send_bulk_different_messages_incorrect(self, a):
        with self.assertRaises(Exception):
            moodle_api.send_message([5, 4, 2], 'TestMessage')

    @patch('requests.post', return_value=MockResponse(200, test_data.test_moodle_course_by_id_field_return))
    def test_get_course_by_id_field(self, a):
        moodle_api.get_course_by_id_field(2)

        a.assert_called_with('DUMMY_MOODLE_URL/core_course_get_courses_by_field',
                             headers={'Content-Type': 'application/json', 'Accept': 'application/json',
                                      'Authorization': 'DUMMY_MOODLE_TOKEN'}, json={'field': 'id', 'value': 2})

    @patch('requests.post', return_value=MockResponse(200, lib_test_data.test_parse_enrolled_users))
    def test_get_enrolled_users(self, a):
        moodle_api.get_enrolled_users(2)

        a.assert_called_with('DUMMY_MOODLE_URL/core_enrol_get_enrolled_users',
                             headers={'Content-Type': 'application/json', 'Accept': 'application/json',
                                      'Authorization': 'DUMMY_MOODLE_TOKEN'}, json={'courseid': 2})

    @patch('requests.post', return_value=MockResponse(200, test_data.test_moodle_get_assignments_return))
    def test_get_assignments(self, a):
        moodle_api.get_assignments([2])

        a.assert_called_with('DUMMY_MOODLE_URL/mod_assign_get_assignments',
                             headers={'Content-Type': 'application/json', 'Accept': 'application/json',
                                      'Authorization': 'DUMMY_MOODLE_TOKEN'},
                             json={'includenotenrolledcourses': 1, 'courseids': [2]})

    @patch('requests.post', return_value=MockResponse(200, test_data.test_moodle_get_assignments_status_return))
    def test_get_assignment_status(self, a):
        moodle_api.get_assignment_status(2, 4)

        a.assert_called_with('DUMMY_MOODLE_URL/core_completion_get_activities_completion_status',
                             headers={'Content-Type': 'application/json', 'Accept': 'application/json',
                                      'Authorization': 'DUMMY_MOODLE_TOKEN'}, json={'courseid': 2, 'userid': 4})

    @patch('requests.post', return_value=MockResponse(200, {}))
    def test_send_query_correct(self, a):
        moodle_api.send_query('dummy_function', {}, 200)

        a.assert_called_with('DUMMY_MOODLE_URL/dummy_function',
                             headers={'Content-Type': 'application/json', 'Accept': 'application/json',
                                      'Authorization': 'DUMMY_MOODLE_TOKEN'}, json={})

    @patch('requests.post', return_value=MockResponse(400))
    def test_send_query_incorrect(self, a):
        with self.assertRaises(Exception):
            moodle_api.send_query('dummy_function', {}, 200)
