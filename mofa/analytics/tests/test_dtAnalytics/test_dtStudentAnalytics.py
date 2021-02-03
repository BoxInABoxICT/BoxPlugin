# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import os
import sys
import json
import unittest
from unittest.mock import patch

from analytics.src.dtAnalytics import dtStudentAnalytics
import analytics.src.lrsConnect as lrs


class BetweenStudentsAnalytics(unittest.TestCase):

    @patch("analytics.src.dtAnalytics.dtStudentAnalytics.runQuery")
    def test_betweenStudentsDifference(self, data_mock):
        """
        Test if the betweenstudent statistics get calculated correctly
        """
        # setup mock
        d = os.path.dirname(os.path.realpath(__file__))
        data_mock.return_value = json.loads(open(f'{d}/queryResult.json').read())

        # setup (manually calculated) validation data and get the function result
        correctResult = [
            # [23, 50, 80, 75]
            {
                "count": 4,
                "max": 80,
                "min": 23,
                "average": 57,
                "median": 62,
                "q1": 36,
                "q3": 78,
                "standarddeviation": 23
            },
            # [65, 83]
            {
                "count": 2,
                "max": 83,
                "min": 65,
                "average": 74,
                "median": 74,
                "q1": 65,
                "q3": 83,
                "standarddeviation": 9
            },
            # [86]
            {
                "count": 1,
                "max": 86,
                "min": 86,
                "average": 86,
                "median": 86,
                "q1": 86,
                "q3": 86,
                "standarddeviation": 0
            }
        ]
        actualResult = dtStudentAnalytics.betweenStudentsDifference(1)

        # check if the correct result and the function result are equal
        self.assertEqual(correctResult, actualResult)

    @patch("analytics.src.dtAnalytics.dtStudentAnalytics.runQuery")
    def test_betweenStudentsDifferenceError(self, data_mock):
        """
        Tests if the betweenStudentdsDifference function passes an error trough unchanged
        """
        # setup mock
        error = json.loads('{"error": "testerror"}')
        data_mock.return_value = error

        # run test
        self.assertEqual(error, dtStudentAnalytics.betweenStudentsDifference(1))


class BetweenStudentAttemptDifferenceAnalytics(unittest.TestCase):

    @patch("analytics.src.dtAnalytics.dtStudentAnalytics.runQuery")
    def test_betweenStudentAttemptDifference(self, data_mock):
        d = os.path.dirname(os.path.realpath(__file__))
        data_mock.return_value = json.loads(open(f'{d}/queryResult.json').read())

        # setup (manually calculated) validation data and get the function result
        correctResult = [
            # [23, 50] -> [65, 83] = [42, 33]
            {
                "count": 2,
                "max": 42,
                "min": 33,
                "average": 38,
                "median": 38,
                "q1": 33,
                "q3": 42,
                "standarddeviation": 4
            },
            # [65] -> [86] = [21]
            {
                "count": 1,
                "max": 21,
                "min": 21,
                "average": 21,
                "median": 21,
                "q1": 21,
                "q3": 21,
                "standarddeviation": 0
            }
        ]
        actualResult = dtStudentAnalytics.betweenStudentAttemptDifference(1)

        # check if the correct result and the function result are equal
        self.assertEqual(correctResult, actualResult)

    @patch("analytics.src.dtAnalytics.dtStudentAnalytics.runQuery")
    def test_betweenStudentAttemptDifferenceError(self, data_mock):
        """
        Tests if the betweenStudentAttemptDifference function passes an error trough unchanged
        """
        # setup mock
        error = json.loads('{"error": "testerror"}')
        data_mock.return_value = error

        # run test
        self.assertEqual(error, dtStudentAnalytics.betweenStudentAttemptDifference(1))


class BestAttemptAnalytics(unittest.TestCase):

    @patch("analytics.src.dtAnalytics.dtStudentAnalytics.runQuery")
    def test_bestAttemptStatistics(self, data_mock):
        # setup mock
        d = os.path.dirname(os.path.realpath(__file__))
        data_mock.return_value = json.loads(open(f'{d}/queryResult.json').read())

        # setup (manually calculated) validation data and get the function result
        correctResult = {
            # [86, 83, 80, 75]
            "count": 4,
            "max": 86,
            "min": 75,
            "average": 81,
            "median": 82,
            "q1": 78,
            "q3": 84,
            "standarddeviation": 4
        }
        actualResult = dtStudentAnalytics.bestAttemptStatistics(1)

        # check if the correct result and the function result are equal
        self.assertEqual(correctResult, actualResult)

    @patch("analytics.src.dtAnalytics.dtStudentAnalytics.runQuery")
    def test_bestAttemptStatisticsError(self, data_mock):
        """
        Tests if the bestAttemptStatistics function passes an error trough unchanged
        """
        # setup mock
        error = json.loads('{"error": "testerror"}')
        data_mock.return_value = error

        # run test
        self.assertEqual(error, dtStudentAnalytics.bestAttemptStatistics(1))


class TestLocalUtils(unittest.TestCase):

    def test_groupByStudentNormal(self):
        """
        Test if the groupByStudent function does the groupby correctly and if the order remains unchanged
        """
        # setup mock
        d = os.path.dirname(os.path.realpath(__file__))
        data = json.loads(open(f'{d}/queryResult.json').read())

        # manually calculate correct result and get the function result
        correctResult = {
            "1": [23, 65, 86],
            "2": [50, 83],
            "3": [80],
            "4": [75]
        }
        actualResult = dtStudentAnalytics.groupByStudent(data)

        # check if the correct result and function result are the same
        self.assertEqual(correctResult, actualResult)

    def test_groupByStudentEmpty(self):
        """
        Test if groupByStudent returns an empty dictionary if there are no statements to group
        """
        result = dtStudentAnalytics.groupByStudent([])
        self.assertEqual({}, result)


class TestRunQuery(unittest.TestCase):

    @patch("analytics.src.dtAnalytics.dtStudentAnalytics.lrs.getSimpleLrsData")
    def test_runQuery(self, lrs_mock):
        """
        Test if runQuery() returns data unaltered.
        """
        lrs_mock.return_value = {"key1": "val1", "key2": "val2"}
        assertDict = {"key1": "val1", "key2": "val2"}

        # not really an exciting test, tested for teh sake of code coverage
        ret = dtStudentAnalytics.runQuery("1")
        self.assertEqual(ret, assertDict)

    @patch("analytics.src.dtAnalytics.dtStudentAnalytics.lrs.getSimpleLrsData")
    def test_runQueryIsError(self, lrs_mock):
        """
        Test if runQuery() returns errors unaltered.
        """
        lrs_mock.return_value = {"error": "Learning Locker Error: 999"}
        assertDict = {"error": "Learning Locker Error: 999"}

        # this test might be more useful if earlier error handling gets added
        ret = dtStudentAnalytics.runQuery("1")
        self.assertEqual(ret, assertDict)
