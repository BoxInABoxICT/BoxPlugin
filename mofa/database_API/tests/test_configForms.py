# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import unittest
from unittest.mock import Mock, patch
from database_API.src.configForms import *
from database_API.lang.en_US.CourseSettings import settingStrings, assistantStrings


class UnitTestStandardFormFunctions(unittest.TestCase):

    def test_constructor(self):
        """
        Test the constructor
        """
        form = StandardForm()

        self.assertEqual(form.status, Status.Default)
        self.assertEqual(form.statusType, StatusType.Default)
        self.assertEqual(form.message, '')
        self.assertIsInstance(form.settings, FormSettingObjects)

    def test_toJSON(self):
        """
        Test the JSON parsing with the default form and mocked settingsObjects
        """
        # create test and validation data
        form = StandardForm()
        validationDict = {'status': 'default', 'statusType': 'default', 'message': '', 'objects': {}}

        # apply mock for FormSettingObjects.generateJSON()
        with patch.object(FormSettingObjects, 'generateJSON', return_value={}):
            # test function
            jsonDict = form.toJSON()

        self.assertEqual(jsonDict, validationDict)


class UnitTestCourseSettingsForm(unittest.TestCase):

    def test_emptyConstructor(self):
        """
        Test to see if an argumentless constructor correctly creates the default form
        """
        form = CourseSettingsForm()

        self.assertEqual(form.status, Status.Default)
        self.assertEqual(form.statusType, StatusType.Default)
        self.assertEqual(form.message, '')
        self.assertIsInstance(form.settings, CourseSettingObjects)

    def test_formConstructionWithData(self):
        """
        Test the JSON parsing in the form constructor
        """
        # create test and validation data
        parseData = [
            {'name': "deadline-enabled", 'value': "true"},
            {'name': "deadline-value", 'value': "10"}
        ]

        settingsObject = {
            "deadline": {
                "title": settingStrings.get("deadline").get("title"),
                "description": settingStrings.get("deadline").get("desc"),
                "enabled": True,
                "currentValue": 10,
                "valueType": "hours"
            }
        }
        validationJson = {"status": "default", "statusType": "default", "message": "", "objects": settingsObject}

        # test functionality
        form = CourseSettingsForm(parseData)
        jsonForm = form.toJSON()

        self.assertEqual(jsonForm, validationJson)

    def test_formConstructionWithInvalidSetting(self):
        """
        Test the construction function with a single invalid setting
        """
        # create test and validation data
        parseData = [
            {'name': "irrelevant-unknown", 'value': "discard this"}
        ]

        settingsObject = {
            "irrelevant": {
                'currentValue': None,
                'description': 'No description available',
                'enabled': None,
                'title': 'Unrecognized setting block',
                'valueType': 'NaN'
            }
        }
        validationJson = {"status": "default", "statusType": "default", "message": "", "objects": settingsObject}

        # test functionality
        form = CourseSettingsForm(parseData)
        jsonForm = form.toJSON()

        self.assertEqual(jsonForm, validationJson)

    def test_parseDataFunction(self):
        """
        Standard parsing of two courseSettings with two attributes each
        """
        # create test and validation data
        data = [
            {"name": "deadline-enabled", "value": "true"},
            {"name": "deadline-value", "value": "48"},
            {"name": "inactivity-value", "value": "8"},
            {"name": "inactivity-enabled", "value": "false"}
        ]

        validationData = {"deadline": {"enabled": True, "value": 48}, "inactivity": {"enabled": False, "value": 8}}

        # test function
        form = StandardForm()
        attrParseMap = CourseSettingsForm.attrParseMap
        parsedData = form.parseData(data, **attrParseMap)

        self.assertEqual(parsedData, validationData)

    def test_parseDataFunction_remove_attr(self):
        """
        Remove unwanted data attributes
        """
        # create test and validation data
        data = [
            {"name": "deadline-enabled", "value": "true"},
            {"name": "deadline-value", "value": "48"},
            {"name": "deadline-unknown", "value": "900"},
        ]

        validationData = {"deadline": {"enabled": True, "value": 48}}

        # test function
        form = StandardForm()
        attrParseMap = CourseSettingsForm.attrParseMap
        parsedData = form.parseData(data, **attrParseMap)

        self.assertEqual(parsedData, validationData)


class IntegrationTestCourseSettingsForm(unittest.TestCase):

    def test_addObject(self):
        """
        Test the function call to CourseSettingObjects' add function
        """
        self.maxDiff = None
        # create test and validation data
        form = CourseSettingsForm()
        validationDict = {"testSetting": (True, 20)}

        # test functionality
        form.addObject("testSetting", True, 20)

        self.assertEqual(form.settings.objects, validationDict)

    def test_updateObject(self):
        """
        Test the updateObject function fo see it it updates correctly
        """
        # create test and validation data
        parseData = [
            {'name': "deadline-enabled", 'value': "true"},
            {'name': "deadline-value", 'value': "10"}
        ]

        validationDict = {"deadline": (False, 15)}

        # test functionality
        form = CourseSettingsForm(parseData)
        form.updateObject("deadline", False, 15)

        self.assertEqual(form.settings.objects, validationDict)

    def test_updateObjectDoesNotExist(self):
        """
        Test the updateObject function with a key that does not exist
        """
        # create test and validation data
        parseData = [
            {'name': "deadline-enabled", 'value': "true"},
            {'name': "deadline-value", 'value': "10"}
        ]

        validationDict = {"deadline": (True, 10)}

        # test functionality
        form = CourseSettingsForm(parseData)
        form.updateObject("thisKeyDoesNotExist", False, 15)

        self.assertEqual(form.settings.objects, validationDict)


class IntegrationTestAssistantSettingsForm(unittest.TestCase):

    def test_formConstructionWithIncompleteData(self):
        """
        Test the JSON parsing in the form constructor, check if missing fields get assigned correctly
        """
        self.maxDiff = None
        # create test and validation data
        parseData = [
            {'name': "new_activity-dbAction", 'value': "add"},
            {'name': "quiz_feedback-dbAction", 'value': "update"},
            {'name': "quiz_feedback-quizId", 'value': "3"},
            {'name': "quiz_feedback-provideFeedback", 'value': "true"},
        ]

        settingsObject = {
            "new_activity": {
                "title": assistantStrings.get("new_activity").get('title'),
                "description": assistantStrings.get("new_activity").get('desc'),
                "dbAction": "add"
            },
            "quiz_feedback": {
                3: {
                    "title": assistantStrings.get("quiz_feedback").get('title'),
                    "description": assistantStrings.get("quiz_feedback").get('desc'),
                    "dbAction": "update",
                    "provideFeedback": True,
                    "scoreThreshold": 55
                }
            }
        }
        validationJson = {"status": "default", "statusType": "default", "message": "", "objects": settingsObject}

        # test functionality
        form = AssistantSettingsForm(parseData)
        jsonForm = form.toJSON()
        self.assertDictEqual(jsonForm, validationJson)

    def test_formConstructionWithInvalidSetting(self):
        """
        Test the construction function with a single invalid setting
        """
        # create test and validation data
        parseData = [
            {'name': "unknown_assistant-unknown", 'value': "discard this"}
        ]

        settingsObject = {
            "unknown_assistant": {
                'title': assistantStrings.get("unknown").get('title'),
                'description': assistantStrings.get("unknown").get('desc'),
            }
        }
        validationJson = {"status": "default", "statusType": "default", "message": "", "objects": settingsObject}

        # test functionality
        form = AssistantSettingsForm(parseData)
        jsonForm = form.toJSON()
        self.assertEqual(jsonForm, validationJson)
