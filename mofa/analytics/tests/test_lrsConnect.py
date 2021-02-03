# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import unittest
import json
import os
import copy

from unittest.mock import MagicMock, patch
from analytics.src import lrsConnect as lrs


class TestLRSQueryFunctions(unittest.TestCase):

    @patch("analytics.src.lrsConnect.lrsRequest")
    def test_getSimpleLrsData(self, lrs_mock):
        """
        Test if getSimpleLrsData appends results correctly
        """
        # Setup mocking function and test data
        d = os.path.dirname(os.path.realpath(__file__))
        f1 = open(f'{d}/statementBatch1.json')
        f2 = open(f'{d}/statementBatch2.json')
        batch1 = MagicMock()
        batch1.text = f1.read()
        batch2 = MagicMock()
        batch2.text = f2.read()
        lrs_mock.side_effect = [batch1, batch2]
        query_empty = lrs.Query()

        # Run the test
        result = lrs.getSimpleLrsData(query_empty)
        self.assertEqual([{}, {}, {}, {}, {}, {}, {}], result)

    @patch("analytics.src.lrsConnect.lrsRequest")
    def test_getSimpleLrsData_Error(self, lrs_mock):
        """
        Test if getSimpleLrsData handles an exception correctly
        """
        # Setup mock
        lrs_mock.side_effect = lrs.LearningLockerException(f'mocked exception has been thrown')

        # Run the test
        result = lrs.getSimpleLrsData(lrs.Query())
        correctResult = {"error": "mocked exception has been thrown"}
        self.assertEqual(correctResult, result)


class TestOperatorFunctions(unittest.TestCase):

    def test_operators(self):
        """
        Tests that the operators give the correct output
        """
        # Equals operator
        self.assertEqual(True, lrs.IS(1, 1))
        self.assertEqual(False, lrs.IS(1, 2))

        # Not equal operator
        self.assertEqual(True, lrs.NOT_IS(1, 2))
        self.assertEqual(False, lrs.NOT_IS(1, 1))

        # Test if element is in parameter set
        self.assertEqual(True, lrs.IN(2, [1, 2, 3]))
        self.assertEqual(False, lrs.IN(2, [1, 3]))

        # Test if element is not in parameter set
        self.assertEqual(True, lrs.NOT_IN(2, [1, 3]))
        self.assertEqual(False, lrs.NOT_IN(2, [1, 2, 3]))

        # Test if parameter is in element
        self.assertEqual(True, lrs.CONTAINS([1, 2, 3], 2))
        self.assertEqual(False, lrs.CONTAINS([1, 3], 2))

        # Test if parameter is not in element
        self.assertEqual(True, lrs.NOT_CONTAINS([1, 3], 2))
        self.assertEqual(False, lrs.NOT_CONTAINS([1, 2, 3], 2))

    def test_operatorWrappers(self):
        """
        Tests that the operator wrappers work correctly
        """
        # Setup test data
        lst = [1, 2, 3, 4]
        testAll = lrs.AllInSet(lrs.IS)(lst, 3)
        testAny = lrs.AnyInSet(lrs.IS)(lst, 3)

        # Test the 'all' operator
        self.assertEqual(testAll, False)

        # Test the 'any' operator
        self.assertEqual(testAny, True)

    def test_attrSelectors(self):
        """
        Tests that the attributes with selectors actually select the correct thing
        """
        # Load test statement
        d = os.path.dirname(os.path.realpath(__file__))
        f = open(f'{d}/testStatement.json')
        stm = json.load(f)

        # Run the selector function for each attribute
        self.assertEqual('{"name": "User 1", "account": {"homePage": "http://moodle.boxinabox.nl", "name": "actor_ID"}}', lrs.Attr.ACTOR["selector"](stm))
        self.assertEqual("verb_ID", lrs.Attr.VERB["selector"](stm))
        self.assertEqual("object_ID", lrs.Attr.ACTIVITY["selector"](stm))
        self.assertEqual(["http://moodle.boxinabox.nl"], lrs.Attr.CONTEXTACTIVITY["selector"](stm))
        self.assertEqual("timestamp", lrs.Attr.TIMESTAMP["selector"](stm))


class TestLrsQuery(unittest.TestCase):

    def test_queryWhere(self):
        """
        Tests if the query.where functions works correctly for different cases
        """
        query = lrs.Query()

        # setup testing data
        startParams = query.params
        finalParams1 = copy.deepcopy(startParams)
        finalParams2 = copy.deepcopy(startParams)
        finalParams1[lrs.Attr.ACTOR["param"]] = {"attr": lrs.Attr.ACTOR, "val": "test1"}
        finalParams2[lrs.Attr.ACTOR["param"]] = {"attr": lrs.Attr.ACTOR, "val": "test2"}
        finalFilters1 = [{"select": lrs.Attr.ACTIVITY["selector"], "op": lrs.NOT_IS, "val": "object_ID"}]

        # Normal case
        testParams1 = query.where(lrs.Attr.ACTOR, lrs.IS, "test1")
        self.assertEqual(finalParams1, testParams1.params)
        self.assertEqual([], query.filters)

        # Param already exists case
        testParams2 = query.where(lrs.Attr.ACTOR, lrs.IS, "test2")
        self.assertEqual(finalParams2, testParams2.params)
        self.assertEqual([], testParams2.filters)

        # Not a param but a filter case
        testParams3 = query.where(lrs.Attr.ACTIVITY, lrs.NOT_IS, "object_ID")
        self.assertEqual(finalParams2, testParams3.params)
        self.assertEqual(finalFilters1, testParams3.filters)

    def test_queryBuild(self):
        """
        Tests if the query.build function works correctly with and without conflicting constraints
        """
        # Test on non-conflicting query
        query1 = lrs.Query()
        query1.where(lrs.Attr.ACTOR, lrs.IS, "actor")
        query1.where(lrs.Attr.VERB, lrs.IS, "verb")
        query1.where(lrs.Attr.ACTIVITY, lrs.IS, "activity")
        query1.where(lrs.Attr.LIMIT, lrs.IS, "limit")
        query1Result = query1.build()
        query1Correct = "/data/xAPI/statements?format=ids&agent=actor&verb=verb&activity=activity&limit=limit"
        self.assertEqual(query1Correct, query1Result)

        # Test on conflicting query
        query2 = lrs.Query()
        query2.where(lrs.Attr.ACTIVITY, lrs.IS, "activity")
        query2.where(lrs.Attr.CONTEXTACTIVITY, lrs.IS, "contextActivity")
        query2Result = query2.build()
        query2Correct = "/data/xAPI/statements?format=ids&related_activities=true&activity=contextActivity"
        self.assertEqual(query2Correct, query2Result)

    def test_queryFixConflict(self):
        """
        Tests if the query.fixConflict function fixes the conflict correctly if there is one and does leaves the query unchanged if there is no conflict
        """
        # Setup query
        query = lrs.Query()
        query.where(lrs.Attr.ACTOR, lrs.IS, "actor")

        # Test if no conflict situation leaves query intact
        correctparams1 = {
            "format": {"attr": lrs.Attr.FORMAT, "val": "ids"},
            "agent": {"attr": lrs.Attr.ACTOR, "val": "actor"}
        }
        self.assertEqual(correctparams1, query.params)
        query.fixConflict(lrs.Attr.ACTOR, lrs.Attr.CONTEXTACTOR)
        self.assertEqual(correctparams1, query.params)

        # Test if a conflict can actually be created
        query.where(lrs.Attr.CONTEXTACTOR, lrs.IS, "contextActor")
        correctparams2 = {
            "format": {"attr": lrs.Attr.FORMAT, "val": "ids"},
            "agent": {"attr": lrs.Attr.ACTOR, "val": "actor"},
            "related_agents": {"attr": lrs.Attr.CONTEXTACTOR, "val": "contextActor"}
        }
        self.assertEqual(correctparams2, query.params)
        self.assertEqual([], query.filters)

        # Test if the conflict is fixed correctly
        query.fixConflict(lrs.Attr.ACTOR, lrs.Attr.CONTEXTACTOR)
        correctparams3 = {
            "format": {"attr": lrs.Attr.FORMAT, "val": "ids"},
            "related_agents": {"attr": lrs.Attr.CONTEXTACTOR, "val": "contextActor"}
        }
        correctfilters = [
            {"select": lrs.Attr.ACTOR["selector"], "op": lrs.IS, "val": "actor"}
        ]
        self.assertEqual(correctparams3, query.params)
        self.assertEqual(correctfilters, query.filters)

    def test_querySelect(self):
        """
        Tests if the query.select function correctly adds the selects to the query
        """
        # Test if selects are empty on init
        query = lrs.Query()
        self.assertEqual([], query.selects)

        # Test if an invalid select is ignored
        query.select(lrs.Attr.FORMAT)
        self.assertEqual([], query.selects)

        # Tests if a valid select is added to the selects list
        query.select(lrs.Attr.ACTOR)
        self.assertEqual([lrs.Attr.ACTOR], query.selects)

        # Test if additional selects are appended to the selects list
        query.select(lrs.Attr.VERB)
        self.assertEqual([lrs.Attr.ACTOR, lrs.Attr.VERB], query.selects)

    def test_querySelectData(self):
        """
        Tests if query.selectData gives the correct output for both empty and non empty select
        """
        # Setup test data
        d = os.path.dirname(os.path.realpath(__file__))
        f = open(f'{d}/testStatement.json')
        stm = json.load(f)
        query = lrs.Query()

        # Check if an empty select results in an empty statement
        self.assertEqual({}, query.selectData(stm))

        # Check if a non-empty select actually selects the correct statements
        query.select(lrs.Attr.VERB, lrs.Attr.ACTIVITY)
        correctResult = {
            lrs.Attr.VERB["key"]: "verb_ID",
            lrs.Attr.ACTIVITY["key"]: "object_ID"
        }
        self.assertEqual(correctResult, query.selectData(stm))

    def test_queryFilterData(self):
        """
        Tests if the query.filterData function works correctly
        """
        # Setup test data
        query = lrs.Query()
        d = os.path.dirname(os.path.realpath(__file__))
        f = open(f'{d}/testStatement.json')
        stm = json.load(f)

        # Test if filters are indeed empty and if statements are accepted if the filters are empty
        self.assertEqual([], query.filters)
        self.assertEqual(True, query.filterData(stm))

        # Test if the filters give a correct positive result
        query.where(lrs.Attr.ACTOR, lrs.CONTAINS, "actor")
        self.assertEqual(True, query.filterData(stm))

        # Test if the filters give a correct negative result
        query.where(lrs.Attr.VERB, lrs.CONTAINS, "viewed")
        self.assertEqual(False, query.filterData(stm))

    def test_queryExecuteSelect(self):
        """
        Tests if the query.executeSelect function works for an empty query, a query with only filters, a query with only selects and a query with both selects and filters
        """
        # Setup test data
        self.maxDiff = None
        d = os.path.dirname(os.path.realpath(__file__))
        f1 = open(f'{d}/testStatement.json')
        f2 = open(f'{d}/testStatement2.json')
        stms = [json.load(f1), json.load(f2)]

        # Test for a completely empty query
        query_empty = lrs.Query()
        self.assertEqual([{}, {}], list(query_empty.executeSelect(stms)))

        # Test for a query that contains only select statements
        query_selectonly = lrs.Query()
        query_selectonly.select(lrs.Attr.ACTOR, lrs.Attr.VERB, lrs.Attr.ACTIVITY)
        query_selectonly_correct = [
            {
                lrs.Attr.ACTOR["key"]: '{"name": "User 1", "account": {"homePage": "http://moodle.boxinabox.nl", "name": "actor_ID"}}',
                lrs.Attr.VERB["key"]: "verb_ID",
                lrs.Attr.ACTIVITY["key"]: "object_ID"
            },
            {
                lrs.Attr.ACTOR["key"]: '{"name": "User 1", "account": {"homePage": "http://moodle.boxinabox.nl", "name": "another_actor_ID"}}',
                lrs.Attr.VERB["key"]: "another_verb_ID",
                lrs.Attr.ACTIVITY["key"]: "another_object_ID"
            }
        ]
        self.assertEqual(query_selectonly_correct, list(query_selectonly.executeSelect(stms)))

        # Test for a query that contains only filter statements
        query_filteronly = lrs.Query()
        query_filteronly.where(lrs.Attr.VERB, lrs.NOT_IS, "verb_ID")
        self.assertEqual([{}], list(query_filteronly.executeSelect(stms)))

        # Test for a query that contains both filter and select statements
        query_combined = lrs.Query()
        query_combined.select(lrs.Attr.ACTOR, lrs.Attr.VERB, lrs.Attr.ACTIVITY)
        query_combined.where(lrs.Attr.VERB, lrs.NOT_IS, "verb_ID")
        query_combined_correct = [
            {
                lrs.Attr.ACTOR["key"]: '{"name": "User 1", "account": {"homePage": "http://moodle.boxinabox.nl", "name": "another_actor_ID"}}',
                lrs.Attr.VERB["key"]: "another_verb_ID",
                lrs.Attr.ACTIVITY["key"]: "another_object_ID"
            }
        ]
        self.assertEqual(query_combined_correct, list(query_combined.executeSelect(stms)))
