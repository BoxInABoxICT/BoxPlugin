# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

import unittest

from analytics.src import utils
import os
import json


class TestUtilFunctions(unittest.TestCase):

    def test_getDate(self):
        """
        Asserts that the getDate function only extracts the date from a timestamp
        """
        # create test and validation data
        testInput = "2020-10-23T12:10:30.906Z"
        correct = "2020-10-23"

        # test function
        result = utils.getDate(testInput)

        # check if the result matches the desired result
        self.assertEqual(correct, result)

    def test_dictAsKvParray(self):
        """
        Asserts that the dictAsKvParray function has the correct output for both empty and non-empty inputs
        """
        # create test and validation data
        testInput = {"a": 1, "b": 2, "c": 3}
        testEmpty = {}
        correctInput = [
            {"key": "a", "value": 1},
            {"key": "b", "value": 2},
            {"key": "c", "value": 3}
        ]
        correctEmpty = []

        # test function
        resultInput = utils.dictAsKvParray(testInput, "key", "value")
        resultEmpty = utils.dictAsKvParray(testEmpty, "key", "value")

        # check if the result matches the desired result
        self.assertEqual(correctInput, resultInput)
        self.assertEqual(correctEmpty, resultEmpty)

    def test_mapDict(self):
        """
        Asserts that the mapDict function has the correct output for both empty and non-empty inputs
        """
        # create test and validation data
        testInput = {"a": 1, "b": 2, "c": 3}
        testEmpty = {}
        correctInput = {"a": 2, "b": 4, "c": 6}
        correctEmpty = {}

        # test function
        resultInput = utils.mapDict(testInput, lambda x: x * 2)
        resultEmpty = utils.mapDict(testEmpty, lambda x: x * 2)

        # check if the result matches the desired result
        self.assertEqual(correctInput, resultInput)
        self.assertEqual(correctEmpty, resultEmpty)

    def test_groupOn(self):
        """
        Asserts that the groupOn function has the correct output for both empty and non-empty inputs and for multiple operators
        """
        # create test and validation data
        testInput = [
            {"key": "a", "value": 1},
            {"key": "b", "value": 2},
            {"key": "c", "value": 3},
            {"key": "a", "value": 4},
            {"key": "b", "value": 5},
            {"key": "c", "value": 6},
            {"key": "a", "value": 7},
            {"key": "b", "value": 8},
            {"key": "c", "value": 9},
        ]
        testEmpty = []
        summedCorrect = {"a": 12, "b": 15, "c": 18}
        concattedCorrect = {"a": [1, 4, 7], "b": [2, 5, 8], "c": [3, 6, 9]}
        emptyCorrect = {}

        # test function
        sumResult = utils.groupOn(
            testInput,
            lambda x: x["key"],
            lambda x: x["value"],
            lambda total, x: total + x["value"]
        )
        concattedResult = utils.groupOn(
            testInput,
            lambda x: x["key"],
            lambda x: [x["value"]],
            lambda total, x: total + [x["value"]]
        )
        emptyResult = utils.groupOn(
            testEmpty,
            lambda x: x["key"],
            lambda x: x["value"],
            lambda total, x: total + x["value"]
        )

        # check if the result matches the desired result
        self.assertEqual(summedCorrect, sumResult)
        self.assertEqual(concattedCorrect, concattedResult)
        self.assertEqual(emptyCorrect, emptyResult)

    def test_any(self):
        """
        Asserts that the any function has the correct output for both empty and non-empty inputs
        """
        # create test and validation data
        testEmpty = []
        testHasEven = [1, 3, 5, 7]
        testHas10 = [1, 10, 21]

        emptyResult = utils.any(testEmpty, lambda x: x % 2 == 0)
        hasevenResult = utils.any(testHasEven, lambda x: x % 2 == 0)
        has10Result = utils.any(testHas10, lambda x: x == 10)

        # check if the result matches the desired output
        self.assertEqual(False, emptyResult)
        self.assertEqual(False, hasevenResult)
        self.assertEqual(True, has10Result)

    def test_id(self):
        """
        Asserts that the id function returns its parameter unchanged
        """
        # check if the result matches the desired result
        self.assertEqual("x", utils.id("x"))
        self.assertEqual(10, utils.id(10))

    def test_hasError(self):
        """
        Asserts that the error function detects errors when they are preesent and does not detect them when they are not present
        """
        # check if the result matches the desired output
        self.assertEqual(False, utils.hasError({}))
        self.assertEqual(False, utils.hasError({"key": "value", "key2": "value2"}))
        self.assertEqual(True, utils.hasError({"key1": "data", "error": "errormsg"}))
        self.assertEqual(True, utils.hasError({"error": "errormsg"}))

    def test_transposeLists(self):
        """
        Asserts that the transposeLists function has the correct output for both empty and non-empty inputs
        """
        # create test and validation data
        testInput = [
            [121, 83, 33, 100, 78, 88, 96, 12],
            [54, 32, 12, 56, 30, 36, 41, 5],
            [21, 61, 0, 96, 50, 58, 73, 11]
        ]
        testDiflength = [
            [1, 1, 1, 1, 1],
            [2, 2, 2, 2],
            [3, 3, 3],
            [4, 4],
            [5]
        ]
        testEmpty = [[], [], []]
        transposedCorrect = [
            [121, 54, 21],
            [83, 32, 61],
            [33, 12, 0],
            [100, 56, 96],
            [78, 30, 50],
            [88, 36, 58],
            [96, 41, 73],
            [12, 5, 11]
        ]
        diflengthCorrect = [
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4],
            [1, 2, 3],
            [1, 2],
            [1]
        ]
        emptyCorrect = IndexError
        result = utils.transposeLists(testInput)
        difResult = utils.transposeLists(testDiflength)

        # check if the result matches the desired output
        self.assertEqual(transposedCorrect, result)
        self.assertEqual(diflengthCorrect, difResult)
        with self.assertRaises(emptyCorrect):
            utils.transposeLists(testEmpty)

    def test_getSetStatistics(self):
        """
        Asserts that the getSetStatistics function has the correct output for both empty and non-empty inputs
        """
        # create test and validation data
        testOdd = [12, 20, 44, 90, 112, 157, 212]
        testEven = [12, 20, 44, 90, 112, 157, 212, 306]
        testSmall = [12, 20, 44, 90]
        testEmpty = []

        oddCorrect = {"count": 7, "average": 92, "min": 12, "max": 212, "q1": 20, "median": 90, "q3": 157, "standarddeviation": 69}
        evenCorrect = {"count": 8, "average": 119, "min": 12, "max": 306, "q1": 32, "median": 101, "q3": 184, "standarddeviation": 95}
        smallCorrect = {"count": 4, "average": 42, "min": 12, "max": 90, "q1": 16, "median": 32, "q3": 67, "standarddeviation": 30}
        emptyCorrect = ZeroDivisionError

        result = utils.getSetStatistics(testOdd)
        evenResult = utils.getSetStatistics(testEven)
        smallResult = utils.getSetStatistics(testSmall)

        # check if the result matches the desired output
        self.assertEqual(oddCorrect, result)
        self.assertEqual(evenCorrect, evenResult)
        self.assertEqual(smallCorrect, smallResult)
        with self.assertRaises(emptyCorrect):
            utils.getSetStatistics(testEmpty)

    def test_getMedian(self):
        """
        Asserts that the getMedian function has the correct output for both empty and non-empty inputs
        """
        # create test and validation data
        testOdd = [12, 20, 44, 90, 112]
        testEven = [12, 20, 44, 90, 112, 157]
        testEmpty = []

        oddCorrect = 44
        evenCorrect = 67
        emptyCorrect = IndexError

        result = utils.getMedian(testOdd)
        evenResult = utils.getMedian(testEven)

        # check if the result matches the desired output
        self.assertEqual(oddCorrect, result)
        self.assertEqual(evenCorrect, evenResult)
        with self.assertRaises(emptyCorrect):
            utils.getMedian(testEmpty)

    def test_getQ1(self):
        """
        Asserts that the getQ1 function has the correct output for both empty and non-empty inputs
        """
        # create test and validation data
        testOdd = [12, 20, 44, 90, 112]
        testEven = [12, 20, 44, 90, 112, 157]
        testEmpty = []

        oddCorrect = 16
        evenCorrect = 20
        emptyCorrect = IndexError

        result = utils.getQ1(testOdd)
        evenResult = utils.getQ1(testEven)

        # check if the result matches the desired output
        self.assertEqual(oddCorrect, result)
        self.assertEqual(evenCorrect, evenResult)
        with self.assertRaises(emptyCorrect):
            utils.getQ1(testEmpty)

    def test_getQ3(self):
        """
        Asserts that the getQ3 function has the correct output for both empty and non-empty inputs
        """
        # create test and validation data
        testOdd = [12, 20, 44, 90, 112]
        testEven = [12, 20, 44, 90, 112, 157]
        testEmpty = []

        oddCorrect = 101
        evenCorrect = 112
        emptyCorrect = IndexError

        result = utils.getQ3(testOdd)
        evenResult = utils.getQ3(testEven)

        # check if the result matches the desired output
        self.assertEqual(oddCorrect, result)
        self.assertEqual(evenCorrect, evenResult)
        with self.assertRaises(emptyCorrect):
            utils.getQ3(testEmpty)

    def test_getMedianpoints(self):
        """
        Asserts that the getMedianpoints function has the correct output for both empty and non-empty inputs
        """
        # create test and validation data
        testOdd = [12, 20, 44, 90, 112]
        testEven = [12, 20, 44, 90, 112, 157]
        testEmpty = []

        oddCorrect = (2, -1)
        evenCorrect = (2, 3)
        emptyCorrect = (-1, 0)

        result = utils.getMedianpoints(testOdd)
        evenResult = utils.getMedianpoints(testEven)
        emptyResult = utils.getMedianpoints(testEmpty)

        # check if the result matches the desired output
        self.assertEqual(oddCorrect, result)
        self.assertEqual(evenCorrect, evenResult)
        self.assertEqual(emptyCorrect, emptyResult)

    def test_getMedianvalue(self):
        """
        Asserts that the getMedianvalue function has the correct output for both empty and non-empty inputs
        """
        # create test and validation data
        testOdd = [12, 20, 44, 90, 112]
        testEven = [12, 20, 44, 90, 112, 157]
        testEmpty = []

        oddPoints = utils.getMedianpoints(testOdd)
        evenPoints = utils.getMedianpoints(testEven)
        emptyPoints = utils.getMedianpoints(testEmpty)

        oddCorrect = 44
        evenCorrect = 67
        emptyCorrect = IndexError

        result = utils.getMedianvalue(testOdd, oddPoints)
        evenResult = utils.getMedianvalue(testEven, evenPoints)

        # check if the result matches the desired output
        self.assertEqual(oddCorrect, result)
        self.assertEqual(evenCorrect, evenResult)
        with self.assertRaises(emptyCorrect):
            utils.getMedianvalue(testEmpty, emptyPoints)

    def test_getSequenceDifference(self):
        """
        Asserts that the getSequenceDifference function has the correct output for both empty and non-empty inputs
        """
        # create test and validation data
        testInput = [12, 20, 44, 90, 112, 157, 212, 306]
        testEmpty = []

        inputCorrect = [8, 24, 46, 22, 45, 55, 94]
        emptyCorrect = []

        # check if the result matches the desired output
        result = utils.getSequenceDifference(testInput)
        emptyResult = utils.getSequenceDifference(testEmpty)
        self.assertEqual(inputCorrect, result)
        self.assertEqual(emptyCorrect, emptyResult)

    def test_getAverageScoreNormal(self):
        """
        Test if the getAverageScore function returns the correct result on an actual statement
        """
        # setup mock
        d = os.path.dirname(os.path.realpath(__file__))
        data = json.loads(open(f'{d}/result_normal.json').read())

        # manually calculate correct result and get the function result
        correctResult = 67.6
        actualResult = utils.getAverageScore(data)

        # check if the correct result and function result are the same
        self.assertEqual(correctResult, actualResult)

    def test_getAverageScoreEmpty(self):
        """
        Test if the getAverageScore function returns 0 when there is no data to take the average of
        """
        # setup mock
        d = os.path.dirname(os.path.realpath(__file__))
        data = json.loads(open(f'{d}/result_empty.json').read())

        # run the function on the empty data
        actualResult = utils.getAverageScore(data)

        # check if the function result is 0
        self.assertEqual(0, actualResult)
