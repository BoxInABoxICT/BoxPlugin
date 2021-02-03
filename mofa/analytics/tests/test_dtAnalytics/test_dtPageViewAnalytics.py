# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import os
import json
import unittest
import unittest.mock as mock
from unittest.mock import MagicMock, patch, mock_open

from analytics.src.dtAnalytics import dtPageViewAnalytics
import analytics.src.lrsConnect as lrs


class TestDtPageViewAnalytics(unittest.TestCase):

    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.loadStudentData")
    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.os.path.isfile")
    def test_dtViewedPages_Error(self, mock_isFile, mock_loadData):
        """
        Test if an error is passed trough unchanged
        """
        # setup mock
        mock_isFile.return_value = True
        error = {"error": "testError"}
        mock_loadData.return_value = error

        # test if the result is correct
        result = dtPageViewAnalytics.dtViewedPages(0, 0)
        self.assertEqual(error, result)

    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.loadStudentData")
    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.getStudentData")
    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.os.path.isfile")
    def test_dtViewedPages_NoFile(self, mock_isFile, mock_getStudentData, mock_loadStudentdata):
        """
        Test if the function that retrieves data is called if and only if the data does not exist yet
        """
        # setup mock
        mock_isFile.side_effect = [False, True]
        checkValue = {"error": "a way to exit the function early"}
        mock_loadStudentdata.return_value = checkValue

        # run function
        result = dtPageViewAnalytics.dtViewedPages(0, 0)

        # assert the results
        self.assertEqual(checkValue, result)
        self.assertTrue(mock_getStudentData.called)

    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.getFeatures")
    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.loadStudentData")
    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.os.path.isfile")
    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.linearRegression")
    def test_dtViewedPages_FilePresent(self, mock_regression, mock_isFile, mock_loadData, mock_getFeatures):
        """
        Test if the function returns the correct result
        """
        # setup mock
        mock_isFile.return_value = True
        mock_loadData.return_value = {"data": "testData"}
        mock_getFeatures.return_value = {"features": [], "scores": []}
        mock_regression.side_effect = [
            {"predRMSE": 54, "num": 1},
            {"predRMSE": 65, "num": 2},
            {"predRMSE": 54, "num": 3},
            {"predRMSE": 34, "num": 4},
            {"predRMSE": 32, "num": 5},
            {"predRMSE": 23, "num": 6},
            {"predRMSE": 65, "num": 7},
            {"predRMSE": 534, "num": 8},
            {"predRMSE": 67, "num": 9},
        ]

        # run function
        result = dtPageViewAnalytics.dtViewedPages(0, 0)
        correct = {"predRMSE": 23, "num": 6}

        # assert result
        self.assertEqual(correct, result)

    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.linear_model.Ridge")
    def test_linearRegression(self, ridge_mock):
        """
        Assert that linearRegression returns the correct result assuming the model is correct
        """
        # setup mock
        regMock = MagicMock()
        regMock.fit = lambda x, y: None
        prediction = [50, 9, 5, 7]
        regMock.predict = lambda x: prediction[:len(x)]
        regMock.coef_ = [10.3, -2.6]
        regMock.intercept_ = 4
        ridge_mock.return_value = regMock

        # setup data
        features = {"page1": [1, 2, 3, 4], "page2": [1, 2, 3, 4]}
        scores = [5, 6, 8, 12]
        medianRes = [10, 10]

        # setup the correct result and calculate the actual result
        correct = {
            "trainingPercentage": 50.0,
            "intercept": 4,
            "medianRMSE": dtPageViewAnalytics.getRMSE(medianRes, scores[2:]),
            "predRMSE": dtPageViewAnalytics.getRMSE(prediction[:2], scores[2:]),
            "pageCoefs": [{"page": "page1", "coef": 10}, {"page": "page2", "coef": -3}]
        }
        result = dtPageViewAnalytics.linearRegression(features, scores, 0.5)

        # check if the result is correct
        self.assertEqual(correct, result)

    def test_getRMSE(self):
        """
        Asserts that the getRMSE function works correctly
        """
        # setup data
        set1 = [3, 6, 8, 5, 7]
        set2 = [2, 6, 8, 3, 5]

        # run calculations
        result = dtPageViewAnalytics.getRMSE(set1, set2)
        correct = 1.3416407864998738
        resultempty = dtPageViewAnalytics.getRMSE([], [])
        correctempty = 0

        # check results
        self.assertEqual(correct, result)
        self.assertEqual(correctempty, resultempty)

    @patch("builtins.open")
    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.getDTdata")
    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.getPageViewData")
    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.groupByStudent")
    def test_getStudentData(self, mock_groupStudent, mock_pageView, mock_getDTdata, mock_openFile):
        """
        Test the correct grouping of values returned by (mocked) functions
        """
        # setup mock and data
        scenarioID = 0
        courseid = 1
        verificationDict = [{"score": 100, "pages": "pageData 1"}, {"score": 90, "pages": "pageData 2"}, {"score": 80, "pages": "pageData 3"}]

        mockedAggergated = {1: {"score": 100, "timestamp": "2021-01-28T13:00:00Z"}, 2: {"score": 90, "timestamp": "2021-01-28T13:00:00Z"}, 3: {"score": 80, "timestamp": "2021-01-28T13:00:00Z"}}
        mock_groupStudent.return_value = mockedAggergated

        mock_pageView.side_effect = ["pageData 1", "pageData 2", "pageData 3"]

        mock_writefile = MagicMock()
        mock_openFile.return_value = mock_writefile

        # check if everything worked
        dtPageViewAnalytics.getStudentData(scenarioID, courseid)
        mock_writefile.write.assert_called_with(json.dumps(verificationDict))

    @patch("builtins.open")
    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.getDTdata")
    def test_getStudentData_Error(self, mock_getDTdata, mock_openFile):
        """
        Test if an error is passed trough unchanged
        """
        # setup mock
        error = {"error": "testError"}
        mock_getDTdata.return_value = error
        mock_writefile = MagicMock()
        mock_openFile.return_value = mock_writefile

        # check if everything worked
        dtPageViewAnalytics.getStudentData(0, 1)
        mock_writefile.write.assert_called_with(json.dumps(error))

    def test_loadStudentData(self):
        """
        Wrapper function containing exclusively standard python functions, left untested for now
        """
        pass

    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.extractFeatures")
    def test_getFeatures(self, mock_extractFeatures):
        """
        Test if sufficient pagevisits returns extracted featuredata correctly
        """
        # setup mock and data
        data = [{"score": 55, "pages": {"1": 1, "2": 1}}, {"score": 55, "pages": {"1": 1}}, {"score": 55, "pages": {"3": 1, "4": 1}}]

        extractedFeaturesMock = {"scores": [55, 55, 55], "features": {
            "1": [1, 1, 0],
            "2": [1, 0, 0],
            "3": [0, 0, 1],
            "4": [0, 0, 1]
        }}
        mock_extractFeatures.return_value = extractedFeaturesMock

        # check if everything worked
        returnVal = dtPageViewAnalytics.getFeatures(data)
        self.assertEquals(returnVal, extractedFeaturesMock)

    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.extractFeatures")
    def test_getFeaturesNoStudentScores(self, mock_extractFeatures):
        """
        Test if insufficient studentcount removes the related page
        """
        # setup mock and data
        assertionData = {"scores": [55, 55, 55], "features": {"1": [1, 1, 0], "2": [1, 0, 0], "3": [0, 0, 1], "4": [0, 0, 1]}}

        data = [{"score": 55, "pages": {"1": 1, "2": 1}}, {"score": 55, "pages": {"1": 1}}, {"score": 55, "pages": {"3": 1, "4": 1}}]
        # pretend no students visited page 5
        extractedFeaturesMock = {"scores": [55, 55, 55], "features": {
            "1": [1, 1, 0],
            "2": [1, 0, 0],
            "3": [0, 0, 1],
            "4": [0, 0, 1],
            "5": [0, 0, 0]
        }}
        mock_extractFeatures.return_value = extractedFeaturesMock

        # check if everything worked
        returnVal = dtPageViewAnalytics.getFeatures(data)
        self.assertEquals(returnVal, assertionData)

    @patch("analytics.src.dtAnalytics.dtPageViewAnalytics.extractFeatures")
    def test_getFeaturesOnePopulairPage(self, mock_extractFeatures):
        """
        Test if all pages remain included with one highly visited page.
        Other pages still get visited by enogh students to be above the treshold.
        """
        # setup mock and data
        assertionData = {"scores": [55, 55, 55], "features": {"1": [1000, 1000, 1000], "2": [1, 0, 0], "3": [0, 0, 1], "4": [0, 0, 1]}}  # assert fails as pages with <5% visit contribution get included as well

        data = [{"score": 55, "pages": {"1": 1000, "2": 1}}, {"score": 55, "pages": {"1": 1000}}, {"score": 55, "pages": {"1": 1000, "3": 1, "4": 1}}]
        extractedFeaturesMock = {"scores": [55, 55, 55], "features": {
            "1": [1000, 1000, 1000],
            "2": [1, 0, 0],
            "3": [0, 0, 1],
            "4": [0, 0, 1]
        }}  # only page 1 should have significant enough visits to be used
        mock_extractFeatures.return_value = extractedFeaturesMock

        # check if everything worked
        returnVal = dtPageViewAnalytics.getFeatures(data)
        self.assertEquals(returnVal, assertionData)

    def test_extractFeatures(self):
        """
        Test correct grouping of page visits
        """
        # setup mock and data
        pages = ["1", "2", "3", "4", "5"]
        dataset = [{"score": 55, "pages": {"1": 1, "2": 1}}, {"score": 55, "pages": {"1": 1}}, {"score": 55, "pages": {"3": 1, "4": 1}}]
        validationset = {"scores": [55, 55, 55], "features": {
            "1": [1, 1, 0],
            "2": [1, 0, 0],
            "3": [0, 0, 1],
            "4": [0, 0, 1],
            "5": [0, 0, 0]
        }}

        # check if everything worked
        returnset = dtPageViewAnalytics.extractFeatures(pages, dataset)
        self.assertEquals(returnset, validationset)

    def test_extractFeaturesNoScores(self):
        """
        Test extraction with the minimum required keys (pages)
        """
        pages = ["1", "2", "3", "4", "5"]
        dataset = [{"pages": {"1": 1, "2": 1}}, {"pages": {"1": 1}}, {"pages": {"3": 1, "4": 1}}]

        validationset = {"scores": [None, None, None], "features": {
            "1": [1, 1, 0],
            "2": [1, 0, 0],
            "3": [0, 0, 1],
            "4": [0, 0, 1],
            "5": [0, 0, 0]
        }}

        returnset = dtPageViewAnalytics.extractFeatures(pages, dataset)
        self.assertEquals(returnset, validationset)

    @patch('analytics.src.utils.getIdFromUrl')
    @patch('analytics.src.lrsConnect.Query')
    def test_getPageViewDataTwoVisitsOnePage(self, mock_LrsQuery, mock_UrlId):
        """
        Test correct parsing of data returned by the lrs.Query object
        Accumulate visits to the same page
        """
        # setup mock and data
        # data represents an extremely trimmed down version of the dataset returned by the lrsQuery
        mockData = [{"timestamp": "2021-01-28T13:00:00.000Z", "activity": "1"}, {"timestamp": "2021-01-27T13:00:00.000Z", "activity": "1"}]
        mock_LrsQuery.return_value.select.return_value.where.return_value.where.return_value.where.return_value.where.return_value.execute.return_value = mockData
        mock_UrlId.side_effect = ["1", "1"]

        validationData = {'1': 2}

        # check if everything worked
        returnData = dtPageViewAnalytics.getPageViewData("irrelevantArg", "irrelevantArg", "2021-01-28T13:00:01Z")
        self.assertEquals(returnData, validationData)

    @patch('analytics.src.utils.getIdFromUrl')
    @patch('analytics.src.lrsConnect.Query')
    def test_getPageViewDataTwoPages(self, mock_LrsQuery, mock_UrlId):
        """
        Test correct parsing of data returned by the lrs.Query object
        Visits to two different pages
        """
        # setup mock and data
        # data represents an extremely trimmed down version of the dataset returned by the lrsQuery
        mockData = [{"timestamp": "2021-01-28T13:00:00.000Z", "activity": "1"}, {"timestamp": "2021-01-28T13:00:00.000Z", "activity": "2"}]
        mock_LrsQuery.return_value.select.return_value.where.return_value.where.return_value.where.return_value.where.return_value.execute.return_value = mockData
        mock_UrlId.side_effect = ["1", "2"]

        validationData = {'1': 1, '2': 1}

        # check if everything worked
        returnData = dtPageViewAnalytics.getPageViewData("irrelevantArg", "irrelevantArg", "2021-01-28T13:00:01Z")
        self.assertEquals(returnData, validationData)

    @patch('analytics.src.utils.getIdFromUrl')
    @patch('analytics.src.lrsConnect.Query')
    def test_getPageViewDataOutdatedData(self, mock_LrsQuery, mock_UrlId):
        """
        Test correct parsing of data returned by the lrs.Query object
        Data is older than the time treshold, should not get added
        """
        # setup mock and data
        # data represents an extremely trimmed down version of the dataset returned by the lrsQuery
        mockData = [{"timestamp": "2021-01-01T13:00:00.000Z", "activity": "1"}]
        mock_LrsQuery.return_value.select.return_value.where.return_value.where.return_value.where.return_value.where.return_value.execute.return_value = mockData
        mock_UrlId.side_effect = ["1"]

        validationData = {}

        # check if everything worked
        returnData = dtPageViewAnalytics.getPageViewData("irrelevantArg", "irrelevantArg", "2021-01-28T13:00:01Z")
        self.assertEquals(returnData, validationData)

    @patch('analytics.src.utils.getIdFromUrl')
    @patch('analytics.src.lrsConnect.Query')
    def test_getPageViewDataFutureData(self, mock_LrsQuery, mock_UrlId):
        """
        Test correct parsing of data returned by the lrs.Query object
        Data is newer than analysis date treshold, should not get added
        """
        # setup mock and data
        # data represents an extremely trimmed down version of the dataset returned by the lrsQuery
        mockData = [{"timestamp": "2021-01-30T13:00:00.000Z", "activity": "1", }]
        mock_LrsQuery.return_value.select.return_value.where.return_value.where.return_value.where.return_value.where.return_value.execute.return_value = mockData
        mock_UrlId.side_effect = ["1"]

        validationData = {}

        # check if everything worked
        returnData = dtPageViewAnalytics.getPageViewData("irrelevantArg", "irrelevantArg", "2021-01-28T13:00:01Z")
        self.assertEquals(returnData, validationData)

    def test_getDTdata(self):
        """
        Untested wrapper function
        """
        pass

    @patch("analytics.src.utils.getAverageScore")
    def test_groupByStudent(self, mock_averageScore):
        """
        Test correct grouping of student data from the lrs dataset
        """
        # setup mock and data
        mock_averageScore.side_effect = [100, 90, 80]

        # data represents an extremely trimmed down version of the data entry stored on the lrs for sake of readability
        data = [{"actor": 1, "timestamp": "2021-01-28T13:00:00Z", "result": "see mock"}, {"actor": 2, "timestamp": "2021-01-28T13:00:00Z", "result": "see mock"}, {"actor": 3, "timestamp": "2021-01-28T13:00:00Z", "result": "see mock"}]
        validation = {1: {"score": 100, "timestamp": "2021-01-28T13:00:00Z"}, 2: {"score": 90, "timestamp": "2021-01-28T13:00:00Z"}, 3: {"score": 80, "timestamp": "2021-01-28T13:00:00Z"}}

        # check if everything worked
        returndata = dtPageViewAnalytics.groupByStudent(data)
        self.assertEquals(returndata, validation)
