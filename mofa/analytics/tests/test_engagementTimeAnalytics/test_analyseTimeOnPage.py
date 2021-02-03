# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

import os
import datetime as dt
import json
import unittest
from unittest.mock import MagicMock, patch

from analytics.src.engagementTimeAnalytics import analyseTimeOnPage
from analytics.src.lrsConnect import LearningLockerException


def mkTime(timestring):
    """
    Syntactic sugar for constructing datetime objects from a string
    """
    return dt.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S%z')


# unit tests
class TestCrawlerFunction(unittest.TestCase):

    def test_simpleTest(self):
        """
        Asserts if a single visit gets properly added
        """
        # create test and validation data
        data = [(mkTime("2020-11-01T11:00:00+01:00"), "1"), (mkTime("2020-11-01T11:05:00+01:00"), "1")]  # day 1, 5 min for page 1
        assertDict = {"1": {dt.date(2020, 11, 1): (data[1][0] - data[0][0], 1)}}

        # test function
        history = dict()
        history = analyseTimeOnPage.dataCrawler(data, history)

        self.assertEqual(history, assertDict)

    def test_twoDates(self):
        """
        Asserts if a page visit on two different dates get added as individual items to the returned dictionary
        """
        # create test and validation data
        data = [
            (mkTime("2020-11-01T11:00:00+01:00"), "1"), (mkTime("2020-11-01T11:05:00+01:00"), "1"),  # day 1, 5 min for page 1
            (mkTime("2020-11-02T11:00:00+01:00"), "1"), (mkTime("2020-11-02T11:05:00+01:00"), "1")   # day 2, 5 min for page 1
        ]
        assertDict = {"1": {dt.date(2020, 11, 1): (data[1][0] - data[0][0], 1),
                            dt.date(2020, 11, 2): (data[3][0] - data[2][0], 1)}}

        # test function
        history = dict()
        history = analyseTimeOnPage.dataCrawler(data, history)

        self.assertEqual(history, assertDict)

    def test_singleDateTwoVisits(self):
        """
        Asserts if a page visit on the same date gets correclty summed in the returned dictionary
        """
        # create test and validation data
        data = [
            (mkTime("2020-11-01T11:00:00+01:00"), "1"), (mkTime("2020-11-01T11:05:00+01:00"), "1"),  # day 1, 5 min for page 1
            (mkTime("2020-11-01T16:00:00+01:00"), "1"), (mkTime("2020-11-01T16:05:00+01:00"), "1")   # day 1, 5 min for page 1 in second visit
        ]
        assertDict = {"1": {dt.date(2020, 11, 1): ((data[1][0] - data[0][0]) + (data[3][0] - data[2][0]), 2)}}

        # test function
        history = dict()
        history = analyseTimeOnPage.dataCrawler(data, history)

        self.assertEqual(history, assertDict)

    def test_singleDataEntry(self):
        """
        Asserts that a single timestamp gets ignored, as at least 2 are nessecary to determine duration
        """
        # create test and validation data
        data = [(mkTime("2020-11-01T11:00:00+01:00"), "1")]
        assertDict = {}

        # test function
        history = dict()
        history = analyseTimeOnPage.dataCrawler(data, history)

        self.assertEqual(history, assertDict)

    def test_nonDestructiveOpsNone(self):
        """
        Asserts that a non empty dictionary getting passed as the 2nd argument returns unaltered when 1st argument is empty
        """
        # create test and validation data
        data = []
        assertDict = {"1": {dt.date(2020, 11, 1): (dt.time(0, 30, 0), 1)}}

        # test function
        history = {"1": {dt.date(2020, 11, 1): (dt.time(0, 30, 0), 1)}}
        history = analyseTimeOnPage.dataCrawler(data, history)

        self.assertEqual(history, assertDict)

    def test_nonDestructiveOpsTwoCourses(self):
        """
        Asserts that a non empty dictionary retains pre-existing data when additional data gets added:
        new pageID key and dict() entry should be added
        """
        # create test and validation data
        data = [(mkTime("2020-11-02T11:00:00+01:00"), "2"), (mkTime("2020-11-02T11:05:00+01:00"), "2")]
        assertDict = {"1": {dt.date(2020, 11, 1): (dt.timedelta(seconds=300), 1)},
                      "2": {dt.date(2020, 11, 2): (data[1][0] - data[0][0], 1)}}

        # test function
        history = {"1": {dt.date(2020, 11, 1): (dt.timedelta(seconds=300), 1)}}
        history = analyseTimeOnPage.dataCrawler(data, history)

        self.assertEqual(history, assertDict)

    def test_nonDestructiveOpsTwoDates(self):
        """
        Asserts that a non empty dictionary retains pre-existing data when additional data gets added:
        new date key and (duration count) tuple should be added
        """
        # create test and validation data
        data = [(mkTime("2020-11-02T11:00:00+01:00"), "1"), (mkTime("2020-11-02T11:05:00+01:00"), "1")]
        assertDict = {"1": {dt.date(2020, 11, 1): (dt.timedelta(seconds=300), 1),
                            dt.date(2020, 11, 2): (data[1][0] - data[0][0], 1)}}

        # test function
        history = {"1": {dt.date(2020, 11, 1): (dt.timedelta(seconds=300), 1)}}
        history = analyseTimeOnPage.dataCrawler(data, history)

        self.assertEqual(history, assertDict)

    def test_nonDestructiveOpsAddition(self):
        """
        Asserts that a non empty dictionary retains pre-existing data when additional data gets added:
        (duration, count) tuple should get increased
        """
        # create test and validation data
        data = [(mkTime("2020-11-01T11:00:00+01:00"), "1"), (mkTime("2020-11-01T11:05:00+01:00"), "1")]
        assertDict = {"1": {dt.date(2020, 11, 1): (dt.timedelta(seconds=300) + (data[1][0] - data[0][0]), 2)}}

        # test function
        history = {"1": {dt.date(2020, 11, 1): (dt.timedelta(seconds=300), 1)}}
        history = analyseTimeOnPage.dataCrawler(data, history)

        self.assertEqual(history, assertDict)

    def test_minTimeNotElapsed(self):
        """
        Asserts that timestamps before min_time do not get added
        """
        # create test and validation data
        data = [(mkTime("2020-11-01T11:00:00+01:00"), "1"), (mkTime("2020-11-01T11:00:01+01:00"), "1")]
        assertDict = {}

        # test function
        history = dict()
        history = analyseTimeOnPage.dataCrawler(data, history)

        self.assertEqual(history, assertDict)

    def test_maxTimeElapsed(self):
        """
        Asserts that timestamps beyond max_time do not get added
        """
        # create test and validation data
        data = [(mkTime("2020-11-01T11:00:00+01:00"), "1"), (mkTime("2020-11-01T12:30:00+01:00"), "1")]
        assertDict = {}

        # test function
        history = dict()
        history = analyseTimeOnPage.dataCrawler(data, history)

        self.assertEqual(history, assertDict)


class TestSortArrayFunction(unittest.TestCase):

    def test_sorted(self):
        """
        asserts the tuples get correctly sorted
        """
        # create test and validation data
        timestamps = [(mkTime("2020-11-05T11:00:00+01:00"), "1"), (mkTime("2020-11-04T11:00:00+01:00"), "2"),
                      (mkTime("2020-11-03T11:00:00+01:00"), "3"), (mkTime("2020-11-02T11:00:00+01:00"), "4"),
                      (mkTime("2020-11-01T11:00:00+01:00"), "5"), (mkTime("2020-11-01T10:00:00+01:00"), "6")]

        assertArray = [(mkTime("2020-11-01T10:00:00+01:00"), "6"), (mkTime("2020-11-01T11:00:00+01:00"), "5"),
                       (mkTime("2020-11-02T11:00:00+01:00"), "4"), (mkTime("2020-11-03T11:00:00+01:00"), "3"),
                       (mkTime("2020-11-04T11:00:00+01:00"), "2"), (mkTime("2020-11-05T11:00:00+01:00"), "1")]

        # test function
        sorting = analyseTimeOnPage.sortArray(timestamps)
        self.assertEqual(sorting, assertArray)


class TestAnalyseModuleVisitTimeFunction(unittest.TestCase):

    @patch('analytics.src.lrsConnect.lrsRequest')
    def test_pipelineCall(self, lrsRequest_mock):
        """
        Standard pipeline call which shouldn't throw any exceptions
        """
        # load test and validation data
        d = os.path.dirname(os.path.realpath(__file__))
        data = [open(f'{d}/statementBatch1.json'), open(f'{d}/statementBatch2.json')]
        validation = json.load(open(f'{d}/validationFile.json'))

        # create a mocked response object for each (expected) lrsRequest() call
        mock_resp = []
        for f in data:
            response = MagicMock()
            response.text = f.read()
            mock_resp.append(response)

        lrsRequest_mock.side_effect = mock_resp

        # test function
        result = analyseTimeOnPage.analyseModuleVisitTime("irrelevant_arg")
        self.assertEqual(result, validation)

    @patch('analytics.src.lrsConnect.lrsRequest')
    def test_pipelineCallException(self, lrsRequest_mock):
        """
        Pipeline call which should catch the LL exception and return a json formatted error message
        """
        # load test and validation data
        validation = {"error": "mocked exception has been thrown"}

        lrsRequest_mock.side_effect = LearningLockerException(f'mocked exception has been thrown')

        # test function
        result = analyseTimeOnPage.analyseModuleVisitTime("irrelevant_arg")
        self.assertEqual(result, validation)
