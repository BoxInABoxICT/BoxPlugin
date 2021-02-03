import unittest
import json
import os

from unittest.mock import MagicMock, patch
from analytics.src.participationAnalytics import distinctPageViews


class TestDistinctPageViews(unittest.TestCase):

    @patch("analytics.src.participationAnalytics.distinctPageViews.runQuery")
    def test_generateData(self, lrs_mock):
        """
        Tests if the analysis is performed correctly
        """
        # Setup mock for database query
        d = os.path.dirname(os.path.realpath(__file__))
        f = open(f'{d}/distinctViewQuery.json')
        lrs_mock.side_effect = [json.load(f)]

        # Run the test
        correct_result = {
            "http://localhost/mod/page/view.php?id=1": 1,
            "http://localhost/mod/page/view.php?id=2": 1,
            "http://localhost/mod/quiz/view.php?id=3": 1,
            "http://localhost/mod/page/view.php?id=5": 1,
            "http://localhost/mod/page/view.php?id=6": 1
        }
        actual_result = distinctPageViews.generateData(2)
        self.assertEqual(correct_result, actual_result)

    @patch("analytics.src.participationAnalytics.distinctPageViews.runQuery")
    def test_generateData_error(self, lrs_mock):
        """
        Tests if an error is passed trough correctly
        """
        # Setup mock for database query
        error = {"error": "mock error"}
        lrs_mock.side_effect = [error]

        # Run test
        self.assertEqual(error, distinctPageViews.generateData(2))
