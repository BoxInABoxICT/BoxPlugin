# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

import datetime
from django.test import TestCase
from courses.models import Course

from database_API.src.CourseSettings.courseSettings import *


class TestInactivityDB(TestCase):

    def testFetch(self):
        """
        Test fetching of correct values from the course entry
        """
        course = Course(name="TestCourse", courseId=2, inactivity=False, deadline=True, hours_before=10, inactivity_time=20, version_time=datetime.datetime(2020, 1, 28))
        course.save()
        validationTuple = (False, 20)
        returnTuple = fetchInactivityParams(2)

        self.assertEqual(returnTuple, validationTuple)

    def testFetchNoCourse(self):
        """
        Test fetching of nonexistent course throws exception
        """
        with self.assertRaises(Course.DoesNotExist):
            returnTuple = fetchInactivityParams(2)

    def testUpdate(self):
        """
        Test updating inactivity settings
        """
        course = Course(name="TestCourse", courseId=2, inactivity=False, deadline=True, hours_before=10, inactivity_time=20, version_time=datetime.datetime(2020, 1, 28))
        course.save()

        updateInactivityParams(2, True, 40)
        course = Course.objects.get(courseId=2)

        self.assertEqual(course.inactivity, True)
        self.assertEqual(course.inactivity_time, 40)
