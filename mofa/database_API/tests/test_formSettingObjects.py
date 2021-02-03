# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import unittest

from database_API.src.formSettingObjects import *
from database_API.lang.en_US.CourseSettings import settingStrings, assistantStrings


class TestCourseSettingObjects(unittest.TestCase):

    def test_add(self):
        """
        Test add functionality
        """
        # Test setup
        CourseObjects = CourseSettingObjects()
        validationDict = {"testSetting": (True, 10)}

        # Execute test
        CourseObjects.add("testSetting", True, 10)

        self.assertEqual(CourseObjects.objects, validationDict)

    def test_add_multipleKeys(self):
        """
        Test multiple consecutive add calls
        """
        # Test setup
        CourseObjects = CourseSettingObjects()
        validationDict = {"testSetting": (True, 10), "testSetting2": (False, 20)}

        # Execute test
        CourseObjects.add("testSetting", True, 10)
        CourseObjects.add("testSetting2", False, 20)

        self.assertEqual(CourseObjects.objects, validationDict)

    def test_add_override(self):
        """
        Test if adding a course setting with existing key (correctly) overrides the previous value
        """
        # Test setup
        CourseObjects = CourseSettingObjects()
        CourseObjects.objects = {"testSetting": (True, 10)}
        validationDict = {"testSetting": (False, 10)}

        # Execute test
        CourseObjects.add("testSetting", False, 10)

        self.assertEqual(CourseObjects.objects, validationDict)

    def test_remove(self):
        """
        Test Remove
        """
        # Test setup
        CourseObjects = CourseSettingObjects()
        CourseObjects.objects = {"testSetting": (True, 10)}
        validationDict = {}

        # Execute test
        CourseObjects.remove("testSetting")

        self.assertEqual(CourseObjects.objects, validationDict)

    def test_get(self):
        """
        Test get with existing key in dictionary
        """
        # Test setup
        CourseObjects = CourseSettingObjects()
        CourseObjects.objects = {"testSetting": (True, 10)}
        validationTuple = (True, 10)

        # Execute test
        tup = CourseObjects.get("testSetting")

        self.assertEqual(tup, validationTuple)

    def test_generateJSON(self):
        """
        Test if formatting of the JSON function is correct
        """
        # Test setup
        self.maxDiff = None
        CourseObjects = CourseSettingObjects()
        CourseObjects.objects = {"testSetting": (True, 10)}
        validationDict = {
            "testSetting": {
                "title": settingStrings.get("testSetting", settingStrings['unknown']).get('title'),
                "description": settingStrings.get("testSetting", settingStrings['unknown']).get('desc'),
                "enabled": True,
                "currentValue": 10,
                "valueType": settingStrings.get("testSetting", settingStrings['unknown']).get('valueType')
            }
        }

        # Execute test
        jsonDict = CourseObjects.generateJSON()

        self.assertEqual(jsonDict, validationDict)


class TestAssistantSettingObjects(unittest.TestCase):

    def test_add_newActivity(self):
        """
        Test adding a single new activity assistant setting object
        """
        # test setup
        AssistantObjects = AssistantSettingObjects()
        validationDict = {AssistantKey.NewActivity: {"dbAction": DbAction.Add}}

        # Execute test
        AssistantObjects.add(AssistantKey.NewActivity, **{"dbAction": DbAction.Add})
        self.assertEqual(AssistantObjects.objects, validationDict)

    def test_add_quizFeedbackIncomplete(self):
        """
        Test adding a quizFeedback object with optional fields not specified
        """
        # test setup
        AssistantObjects = AssistantSettingObjects()
        validationDict = {
            AssistantKey.QuizFeedback: {
                1: {
                    'dbAction': DbAction.Add,
                    'provideFeedback': True,
                    'scoreThreshold': 55
                }
            }
        }

        # Execute test
        AssistantObjects.add(AssistantKey.QuizFeedback, **{"dbAction": DbAction.Add, 'quizId': 1})
        self.assertEqual(AssistantObjects.objects, validationDict)

    def test_add_quizFeedback(self):
        """
        Test adding a quizFeedback object with optional fields specified
        """
        # test setup
        AssistantObjects = AssistantSettingObjects()
        validationDict = {
            AssistantKey.QuizFeedback: {
                1: {
                    'dbAction': DbAction.Add,
                    'provideFeedback': False,
                    'scoreThreshold': 75
                }
            }
        }

        # Execute test
        AssistantObjects.add(AssistantKey.QuizFeedback, **{"dbAction": DbAction.Add, 'quizId': 1, 'provideFeedback': False, 'scoreThreshold': 75})
        self.assertEqual(AssistantObjects.objects, validationDict)

    def test_add_unknownAssistant(self):
        """
        Test adding a unspecified object key adds unknown object with 'Error' db action
        """
        # test setup
        AssistantObjects = AssistantSettingObjects()
        validationDict = {
            AssistantKey.Unknown: {
                'dbAction': DbAction.Error
            }
        }

        # Execute test
        AssistantObjects.add(AssistantKey.Unknown, **{"dbAction": DbAction.Add})
        self.assertEqual(AssistantObjects.objects, validationDict)

    def test_updateNewActivityObject(self):
        """
        Test updating newActivity object
        """
        # test setup
        AssistantObjects = AssistantSettingObjects()
        AssistantObjects.objects = {AssistantKey.NewActivity: {"dbAction": DbAction.Add}}
        validationDict = {AssistantKey.NewActivity: {"dbAction": DbAction.Update}}

        # Execute test
        AssistantObjects.update(AssistantKey.NewActivity, **{"dbAction": DbAction.Update})
        self.assertEqual(AssistantObjects.objects, validationDict)

    def test_updatequizFeedbackObject(self):
        """
        Test updating quizFeedback object
        """
        # test setup
        AssistantObjects = AssistantSettingObjects()
        originalDict = {
            AssistantKey.QuizFeedback: {
                1: {
                    'dbAction': DbAction.Fetch,
                    'provideFeedback': True,
                    'scoreThreshold': 55
                },
                2: {
                    'dbAction': DbAction.Fetch,
                    'provideFeedback': True,
                    'scoreThreshold': 10
                }
            }
        }
        AssistantObjects.objects = originalDict

        validationDict = {
            AssistantKey.QuizFeedback: {
                1: {
                    'dbAction': DbAction.Fetch,
                    'provideFeedback': True,
                    'scoreThreshold': 55
                },
                2: {
                    'dbAction': DbAction.Update,
                    'provideFeedback': False,
                    'scoreThreshold': 75
                }
            }
        }

        self.maxDiff = None
        # Execute test
        AssistantObjects.update(AssistantKey.QuizFeedback, **{"dbAction": DbAction.Update, 'quizId': 2, 'provideFeedback': False, 'scoreThreshold': 75})
        self.assertEqual(AssistantObjects.objects, validationDict)

    def test_removeNewActivity(self):
        """
        Test removing quizFeedback object
        """
        # test setup
        AssistantObjects = AssistantSettingObjects()
        AssistantObjects.objects = {AssistantKey.NewActivity: {"dbAction": DbAction.Add}}
        validationDict = {}

        # Execute test
        AssistantObjects.remove(AssistantKey.NewActivity)
        self.assertEqual(AssistantObjects.objects, validationDict)

    def test_removeQuizFeedback(self):
        """
        Test removing quizFeedback object
        """
        # test setup
        AssistantObjects = AssistantSettingObjects()
        AssistantObjects.objects = {
            AssistantKey.QuizFeedback: {
                1: {
                    'dbAction': DbAction.Add,
                    'provideFeedback': False,
                    'scoreThreshold': 75
                }
            }
        }
        validationDict = {}

        # Execute test
        AssistantObjects.remove(AssistantKey.QuizFeedback, 1)
        self.assertEqual(AssistantObjects.objects, validationDict)

    def test_removeSingleQuizFeedback(self):
        """
        Test removing a single quizFeedback object from the datastructure
        """
        # test setup
        AssistantObjects = AssistantSettingObjects()
        AssistantObjects.objects = {
            AssistantKey.QuizFeedback: {
                1: {
                    'dbAction': DbAction.Add,
                    'provideFeedback': False,
                    'scoreThreshold': 75
                },
                2: {
                    'dbAction': DbAction.Add,
                    'provideFeedback': False,
                    'scoreThreshold': 75
                }
            }
        }
        validationDict = {
            AssistantKey.QuizFeedback: {
                1: {
                    'dbAction': DbAction.Add,
                    'provideFeedback': False,
                    'scoreThreshold': 75
                }
            }
        }

        # Execute test
        AssistantObjects.remove(AssistantKey.QuizFeedback, 2)
        self.assertEqual(AssistantObjects.objects, validationDict)

    def test_removeQuizFeedbackIdMismatch(self):
        """
        Test removing quizFeedback object with wrong id has no side effects
        """
        # test setup
        AssistantObjects = AssistantSettingObjects()
        AssistantObjects.objects = {
            AssistantKey.QuizFeedback: {
                1: {
                    'dbAction': DbAction.Add,
                    'provideFeedback': False,
                    'scoreThreshold': 75
                }
            }
        }
        validationDict = {
            AssistantKey.QuizFeedback: {
                1: {
                    'dbAction': DbAction.Add,
                    'provideFeedback': False,
                    'scoreThreshold': 75
                }
            }
        }

        # Execute test
        AssistantObjects.remove(AssistantKey.QuizFeedback, 2)
        self.assertEqual(AssistantObjects.objects, validationDict)

    def test_generateJSON(self):
        """
        Test if he merging of language and setting k,v pairs maintain correct structure
        """
        AssistantObjects = AssistantSettingObjects()
        assistants = {
            AssistantKey.NewActivity: {
                "dbAction": DbAction.Add
            },
            AssistantKey.QuizFeedback: {
                3: {
                    "dbAction": DbAction.Update,
                    "provideFeedback": True,
                    "scoreThreshold": 55
                }
            },
            AssistantKey.Unknown: {
                "dbAction": DbAction.Error
            }
        }
        AssistantObjects.objects = assistants

        validationDict = {
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
            },
            "unknown_assistant": {
                "title": assistantStrings.get("unknown").get('title'),
                "description": assistantStrings.get("unknown").get('desc'),
            }
        }
        self.maxDiff = None
        jsonDict = AssistantObjects.generateJSON()
        self.assertEqual(jsonDict, validationDict)
