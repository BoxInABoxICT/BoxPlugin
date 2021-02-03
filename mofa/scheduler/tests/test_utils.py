# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
from unittest.mock import call, patch

from courses.models import Course
from django.test import TestCase
from scheduler import utils
from scheduler.tests.test_main_scheduler import make_test_course

from . import test_data


class UtilsTest(TestCase):

    @patch('builtins.print')
    def test_get_course_from_db(self, print_mock):
        # Test without a course in the database
        result1 = utils.get_course_from_db(2)
        print_mock.assert_called_with("Course: 2 could not be found in Course when searched in get_course_from_db")
        print_mock.assert_called_once()

        self.assertIs(result1, None)

        # Test with course in the database
        make_test_course(course_id=2)
        result2 = utils.get_course_from_db(2)

        self.assertEqual(len(Course.objects.filter(courseId=2)), 1)
        self.assertEqual(result2, Course.objects.get(courseId=2))

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_ended)
    @patch('time.time', return_value=1637276900)
    def test_check_if_ended_with_ended(self, time, get_course_by_id):
        self.assertEqual(utils.check_if_ended(2), True)

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_live)
    @patch('time.time', return_value=1637276399)
    def test_check_if_ended_with_live(self, time, get_course_by_id):
        self.assertEqual(utils.check_if_ended(2), False)
