# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

import unittest
from unittest.mock import Mock, MagicMock, patch

from enum import Enum
from database_API.src.configForms import *

from database_API.src.CourseSettings.courseSettings import *


class TestCourseFunctions(unittest.TestCase):

    @patch('database_API.src.CourseSettings.courseSettings.fetchInactivityParams')
    @patch('database_API.src.CourseSettings.courseSettings.fetchDeadlineParams')
    def testFetch(self, deadline_mock, inactivity_mock):
        """
        Test if the fetch switch returns a correct form
        """
        form = CourseSettingsForm()
        deadline_mock.return_value = (True, 10)
        inactivity_mock.return_value = (False, 0)

        validationDict = {
            "deadline": (True, 10),
            "inactivity": (False, 0)
        }

        fetchCourseSettings(1, form)

        self.assertTrue(deadline_mock.called)
        self.assertTrue(inactivity_mock.called)

        self.assertEquals(form.status, Status.Success)
        self.assertEquals(form.statusType, StatusType.Fetch)

        self.assertEquals(form.settings.objects, validationDict)

    @patch('database_API.src.CourseSettings.courseSettings.fetchInactivityParams')
    @patch('database_API.src.CourseSettings.courseSettings.fetchDeadlineParams')
    @patch('database_API.src.CourseSettings.courseSettings.updateInactivityParams')
    @patch('database_API.src.CourseSettings.courseSettings.updateDeadlineParams')
    def testEmptyUpdate(self, deadline_mock, inactivity_mock, fetchDeadline_mock, fetchInactivity_mock):
        """
        Test update function without any update arguments
        """
        parseData = []
        form = CourseSettingsForm(parseData)
        fetchDeadline_mock.return_value = (True, 20)
        fetchInactivity_mock.return_value = (True, 30)

        validationDict = {
            "deadline": (True, 20),
            "inactivity": (True, 30)
        }

        updateCourseSettings(1, form)

        self.assertFalse(deadline_mock.called)
        self.assertFalse(inactivity_mock.called)
        self.assertTrue(fetchDeadline_mock.called)
        self.assertTrue(fetchInactivity_mock.called)

        self.assertEquals(form.status, Status.Success)
        self.assertEquals(form.statusType, StatusType.Update)

        self.assertEquals(form.settings.objects, validationDict)

    @patch('database_API.src.CourseSettings.courseSettings.fetchInactivityParams')
    @patch('database_API.src.CourseSettings.courseSettings.fetchDeadlineParams')
    @patch('database_API.src.CourseSettings.courseSettings.updateInactivityParams')
    @patch('database_API.src.CourseSettings.courseSettings.updateDeadlineParams')
    def testDeadlineUpdate(self, deadline_mock, inactivity_mock, fetchDeadline_mock, fetchInactivity_mock):
        """
        Test update function without any update arguments
        """
        parseData = [
            {'name': "deadline-enabled", 'value': "true"},
            {'name': "deadline-value", 'value': "10"}
        ]
        form = CourseSettingsForm(parseData)

        fetchDeadline_mock.return_value = (True, 10)
        fetchInactivity_mock.return_value = (True, 30)

        validationDict = {
            "deadline": (True, 10),
            "inactivity": (True, 30)
        }

        updateCourseSettings(1, form)

        self.assertTrue(deadline_mock.called)
        self.assertFalse(inactivity_mock.called)
        self.assertTrue(fetchDeadline_mock.called)
        self.assertTrue(fetchInactivity_mock.called)

        self.assertEquals(form.status, Status.Success)
        self.assertEquals(form.statusType, StatusType.Update)

        self.assertEquals(form.settings.objects, validationDict)

    @patch('database_API.src.CourseSettings.courseSettings.fetchInactivityParams')
    @patch('database_API.src.CourseSettings.courseSettings.fetchDeadlineParams')
    @patch('database_API.src.CourseSettings.courseSettings.updateInactivityParams')
    @patch('database_API.src.CourseSettings.courseSettings.updateDeadlineParams')
    def testInactivityUpdate(self, deadline_mock, inactivity_mock, fetchDeadline_mock, fetchInactivity_mock):
        """
        Test update function without any update arguments
        """
        parseData = [
            {'name': "inactivity-enabled", 'value': "False"},
            {'name': "inactivity-value", 'value': "20"}
        ]
        form = CourseSettingsForm(parseData)

        fetchDeadline_mock.return_value = (True, 10)
        fetchInactivity_mock.return_value = (False, 20)

        validationDict = {
            "deadline": (True, 10),
            "inactivity": (False, 20)
        }

        updateCourseSettings(1, form)

        self.assertFalse(deadline_mock.called)
        self.assertTrue(inactivity_mock.called)
        self.assertTrue(fetchDeadline_mock.called)
        self.assertTrue(fetchInactivity_mock.called)

        self.assertEquals(form.status, Status.Success)
        self.assertEquals(form.statusType, StatusType.Update)

        self.assertEquals(form.settings.objects, validationDict)
