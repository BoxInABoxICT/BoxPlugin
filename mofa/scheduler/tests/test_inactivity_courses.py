# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Test the methods of the inactivity_courses.py file."""
import datetime as dt
import json
import unittest
from unittest.mock import patch

from scheduler import inactivity_courses as ic
from scheduler import main_scheduler
from scheduler.models import InactivityNotificationSent
from . import test_data


class TestCalculateDate(unittest.TestCase):
    def test_calculate_date(self):
        self.assertEqual(ic.calculate_date(dt.date(2019, 11, 4), 7), dt.date(2019, 10, 28))

    def test_students_not_viewed(self):
        # check database
        test_student_entry = InactivityNotificationSent('1', json.dumps({'1': '1', '2': '1'}))
        test_student_entry.save()
        self.assertEqual(set(ic.students_not_viewed(['1', '2', '3', '4', '5'], ['3', '4'], 1)), {'5'})

    def test_get_message(self):
        self.assertEqual(
            ic.get_message(
                "BeginningCourse", 7), 'You have not viewed the course \"BeginningCourse\" in 7 day(s). '
                                       'We advise you to stay active, so that you will not miss anything.')

    @patch('assistants.moodle.send_bulk_messages')
    def test_send_message(self, a):
        ic.send_message(['3', '2'], "test")

        self.assertEqual(a.call_count, 1)
        a.assert_called_with({'3', '2'}, 'test')

    @patch('time.time', return_value=1606487381)
    @patch('scheduler.inactivity_courses.check_if_older_than', return_value=True)
    @patch('assistants.moodle.get_enrolled_users', return_value=test_data.test_inactivity_get_enrolled_users)
    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_live)
    @patch('assistants.moodle.send_bulk_messages')
    @patch('assistants.learning_locker.get_viewed_courses', return_value=test_data.test_learning_locker_viewed_course)
    def test_create_job(self, a, b, c, d, e, f):
        ic.create_job(1, 7, main_scheduler.main_scheduler)
        self.assertEqual(c.call_count, 2)
        b.assert_called_with(
            {'5', '3', '4'},
            'You have not viewed the course \"No view course\" in 7 day(s). We advise you to '
            'stay active, so that you will not miss anything.')

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_young)
    @patch('time.time', return_value=1606487381)
    def test_check_if_older_than_with_young(self, time, get_course_by_id):
        self.assertEqual(ic.check_if_older_than(7, 2), False)

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_old)
    @patch('time.time', return_value=1606487381)
    def test_check_if_older_than_with_old(self, time, get_course_by_id):
        self.assertEqual(ic.check_if_older_than(7, 2), True)

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_ended)
    @patch('time.time', return_value=1646487381)
    def test_delete_course(self, time, b):
        test_entry = InactivityNotificationSent('1', json.dumps({'1': '1', '2': '1'}))
        test_entry.save()
        ic.create_job(1, 7, main_scheduler.main_scheduler)

        self.assertFalse(InactivityNotificationSent.objects.filter(pk=1).exists())
