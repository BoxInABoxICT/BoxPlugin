# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

from enum import Enum
from database_API.lang.en_US.CourseSettings import settingStrings, assistantStrings


class AssistantKey(Enum):
    """
    Enum class representing the different Assistant types able to be added to the course
    """
    NewActivity = "new_activity"
    QuizFeedback = "quiz_feedback"
    Unknown = "unknown_assistant"


class DbAction(Enum):
    Add = "add"
    Update = "update"
    Remove = "remove"
    Fetch = "fetch"
    Error = "error"


class FormSettingObjects():
    def generateJSON(self):
        return {}


class CourseSettingObjects(FormSettingObjects):

    def __init__(self):
        self.objects = {}

    def add(self, settingName, mode, value):
        """
        Adds/overrides a settings object for a course setting to the datastructure. \n
        :settingName: key of the setting object to add. \t
        :type: str \n
        :mode: Mode of the setting (enabled/disabled). \t
        :type: bool \n
        :value: Value associated with the setting. \t
        :type: int \n
        """
        obj = (mode, value)
        self.objects[settingName] = obj

    def remove(self, settingName):
        """
        Remove a settings object for a course setting from the datastructure. \n
        :settingName: key of the setting object to remove. \t
        :type: str \n
        """
        del self.objects[settingName]

    def get(self, settingName):
        """
        Fetches a settings object for a course setting from the datastructure, if it exists. \n
        :settingName: key of the setting object to fetch. \t
        :type: str \n
        :returns: The settings for the settingName key, None if it doesn't exist. \t
        :rtype: tuple(bool, int)
        """
        return self.objects.get(settingName)

    def generateJSON(self):
        """
        Converts all the settings object into a dictionary following the json format \n
        :returns: Json formatted dict. \t
        :rtype: dict \n
        """
        jsonDict = {}
        for settingName in self.objects.keys():
            obj = self.objects.get(settingName)
            if(obj is not None):
                settingDict = {
                    "title": settingStrings.get(settingName, settingStrings['unknown']).get('title'),
                    "description": settingStrings.get(settingName, settingStrings['unknown']).get('desc'),
                    "enabled": obj[0],
                    "currentValue": obj[1],
                    "valueType": settingStrings.get(settingName, settingStrings['unknown']).get('valueType')
                }
                jsonDict[settingName] = settingDict
            else:
                continue
        return jsonDict


class AssistantSettingObjects(FormSettingObjects):

    def __init__(self):
        self.objects = {}

    def add(self, assistantKey, **kwargs):
        """
        Add a settings object for an assistant's settings to the datastructure. \t
        :assistantKey: key of the assistant setting object to add. \t
        :type: AssistantKey \n
        :kwargs: k,v pairs of assistant setting attributes. \t
        :type: dict \n
        """
        newSettingObj = self.__assistantSwitch(assistantKey, **kwargs)
        if(assistantKey == AssistantKey.NewActivity):  # only one newActivityAssistant is allowed per course so it can always be (over)written
            self.objects[assistantKey] = newSettingObj
        elif(assistantKey == AssistantKey.QuizFeedback):   # quiz feedback can have multiple assistants per course, so merge dictionaries
            d = {**self.objects.get(assistantKey, {}), **newSettingObj}
            self.objects[assistantKey] = d
        else:
            self.objects[AssistantKey.Unknown] = newSettingObj

    def update(self, assistantKey, **kwargs):
        """
        Update a settings object for an assistant's settings in the datastructure with provided arguments. \t
        :assistantKey: key of the assistant setting object to add. \t
        :type: AssistantKey \n
        :kwargs: k,v pairs of assistant setting attributes. \t
        :type: dict \n
        """
        updatedSettings = self.__assistantSwitch(assistantKey, **kwargs)

        if(assistantKey == AssistantKey.NewActivity):  # only one newActivityAssistant is allowed per course so overwrite old settings
            self.objects[assistantKey] = updatedSettings
        elif(assistantKey == AssistantKey.QuizFeedback):   # check for quizId for which settingsObj needs to be updated
            quizId = kwargs.get('quizId')
            if(quizId in self.objects[assistantKey]):   # only add/overwrite the settings if a previous setting object exists
                self.objects[assistantKey] = {**self.objects[assistantKey], **updatedSettings}
        else:
            return

    def remove(self, assistantKey, identifier=None):
        """
        Remove a setting object from the datastructure if present. \n
        :assistantKey: Key of the assistant setting object to add. \t
        :type: AssistantKey \n
        :identifier: Identifier for the setting object, which is required for some objects \t
        :type: int \n
        """
        if(assistantKey == AssistantKey.NewActivity):
            del self.objects[assistantKey]
        elif(assistantKey == AssistantKey.QuizFeedback and identifier is not None):
            if(self.objects[assistantKey].get(identifier) is not None):
                del self.objects[assistantKey][identifier]
                if(self.objects[assistantKey] == {}):
                    del self.objects[assistantKey]
        else:
            return

    def get(self, assistantKey, identifier=None):
        """
        Search for a setting object from the datastructure if present. \n
        :assistantKey: Key of the assistant setting object to get. \t
        :type: AssistantKey \n
        :identifier: Identifier for the setting object, which is required for some objects \t
        :type: int \n
        :returns: The dictionary containing the assistant setting(s) attributes \t
        :rtype: dict \n
        """
        if(assistantKey == AssistantKey.NewActivity):
            return self.objects.get(assistantKey)
        elif(assistantKey == AssistantKey.QuizFeedback):
            objs = self.objects.get(assistantKey)
            if(identifier is not None and objs is not None):
                return objs.get(identifier)
            else:   # return entire assistant dictionary if no identifier is specified
                return objs
        else:
            return None

    def generateJSON(self):
        """
        Converts all the settings object into a dictionary following the json format \n
        :returns: Json formatted dict. \t
        :rtype: dict \n
        """
        jsonDict = {}
        for assistantKey in self.objects.keys():
            lang = {
                "title": assistantStrings.get(assistantKey.value, assistantStrings['unknown']).get('title'),
                "description": assistantStrings.get(assistantKey.value, assistantStrings['unknown']).get('desc'),
            }
            if(assistantKey == AssistantKey.NewActivity):
                settings = self.objects[assistantKey]
                settings['dbAction'] = settings['dbAction'].value    # cast enum type to string
                jsonDict[assistantKey.value] = {**lang, **settings}  # join language strings with attributes
            elif(assistantKey == AssistantKey.QuizFeedback):      # quizfeedback has multiple assistants per course, add lang strings to each one individually
                settings = self.objects[assistantKey]
                appendedSettings = {}
                for st in settings.keys():
                    settings[st]['dbAction'] = settings[st]['dbAction'].value   # cast enum type to string
                    appendedSettings[st] = {**lang, **settings[st]}
                jsonDict[assistantKey.value] = appendedSettings
            else:
                jsonDict[assistantKey.value] = lang
        return jsonDict

    def __assistantSwitch(self, assistantKey, **kwargs):
        """
        Switch for creating the new settingobjects per assistant
        """
        if(assistantKey == AssistantKey.NewActivity):
            return self.__mkNewActivityObj(**kwargs)
        elif(assistantKey == AssistantKey.QuizFeedback):
            return self.__mkQuizFeedbackObj(**kwargs)
        else:
            return {'dbAction': DbAction.Error}

    def __mkNewActivityObj(self, **kwargs):
        """
        Creates a setting object for the new activity assistant. \t
        Sanitizes the passed kwargs by only retaining the dbAction attribute. \n
        :kwargs: All specified setting attributes for this assistant setting object. \t
        :type: dict \n
        """
        obj = {
            'dbAction': kwargs.get('dbAction')
        }
        return obj

    def __mkQuizFeedbackObj(self, **kwargs):
        """
        Creates a setting object for the quiz feedback assistant with the unique identifier of quizId as a key. \n
        :kwargs: all settings attributes for this assistant setting object. \t
        :type: dict \n
        """
        quizId = kwargs.get('quizId')
        if(quizId is not None):
            obj = {
                quizId: {
                    'dbAction': kwargs.get('dbAction'),
                    'provideFeedback': kwargs.get('provideFeedback', True),
                    'scoreThreshold': kwargs.get('scoreThreshold', 55)
                }
            }
            return obj
        else:
            return None
