# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import os
import sys
import json
import unittest
from unittest.mock import MagicMock, patch

from analytics.src.genericAnalytics import analytics
import analytics.src.lrsConnect as lrs


class TestCountStatements(unittest.TestCase):

    @patch("analytics.src.genericAnalytics.analytics.getViewHistory")
    def test_countViewedStatements(self, data_mock):
        """
        Test if statements get counted correctly
        """
        d = os.path.dirname(os.path.realpath(__file__))
        data_mock.return_value = json.loads(open(f'{d}/testData.json').read())

        ret = analytics.countViewedStatements("")
        self.assertEqual(ret["count"], 12)

    @patch("analytics.src.genericAnalytics.analytics.getViewHistory")
    def test_countViewedStatementsError(self, data_mock):
        """
        Test if statements get counted correctly
        """
        data_mock.return_value = {"error": "Learning Locker Error: 999"}
        assertDict = {"error": "Learning Locker Error: 999"}

        ret = analytics.countViewedStatements("")
        self.assertEqual(ret, assertDict)


class TestGenerateViewedHistory(unittest.TestCase):

    @patch("analytics.src.genericAnalytics.analytics.getViewHistory")
    def test_generateViewedHistory(self, data_mock):
        """
        Test to see if all pages get returned when querying a non existent (-1) coursePage.
        """
        d = os.path.dirname(os.path.realpath(__file__))
        data_mock.return_value = json.loads(open(f'{d}/testData.json').read())
        assertDict = {"http://localhost/course/view.php?id=1": [{"count": 3, "date": "2020-11-01"}, {"count": 1, "date": "2020-11-02"}],
                      "http://localhost/course/view.php?id=2": [{"count": 4, "date": "2020-11-01"}],
                      "http://localhost/course/view.php?id=3": [{"count": 4, "date": "2020-11-01"}]}

        ret = analytics.generateViewedHistory("-1")
        self.assertEqual(ret, assertDict)

    @patch("analytics.src.genericAnalytics.analytics.getViewHistory")
    def test_generateViewedHistoryError(self, data_mock):
        """
        Test if error data aborts further analysis without causing exceptions.
        """
        data_mock.return_value = {"error": "Learning Locker Error: 999"}
        assertDict = {"error": "Learning Locker Error: 999"}

        ret = analytics.getViewHistory("1")
        self.assertEqual(ret, assertDict)


class TestGetViewedHistory(unittest.TestCase):

    @patch("analytics.src.genericAnalytics.analytics.lrs.getSimpleLrsData")
    def test_getViewedHistory(self, lrs_mock):
        """
        Test if getViewedHistory() returns data unaltered.
        """
        lrs_mock.return_value = {"key1": "val1", "key2": "val2"}
        assertDict = {"key1": "val1", "key2": "val2"}

        # not really an exciting test, tested for teh sake of code coverage
        ret = analytics.getViewHistory("1")
        self.assertEqual(ret, assertDict)

    @patch("analytics.src.genericAnalytics.analytics.lrs.getSimpleLrsData")
    def test_getViewedHistoryIsError(self, lrs_mock):
        """
        Test if getViewedHistory() returns errors unaltered.
        """
        lrs_mock.return_value = {"error": "Learning Locker Error: 999"}
        assertDict = {"error": "Learning Locker Error: 999"}

        # this test might be more useful if earlier error handling gets added
        ret = analytics.getViewHistory("1")
        self.assertEqual(ret, assertDict)
