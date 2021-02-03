# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

from enum import Enum

from database_API.src.formSettingObjects import *
from database_API.lang.en_US.CourseSettings import settingStrings, assistantStrings


class Status(Enum):
    Error = 'error'
    Success = 'success'
    Default = 'default'


class StatusType(Enum):
    Fetch = 'fetch'
    Update = 'update'
    Default = 'default'


class StandardForm():
    """
    Superclass used for representing and returning the status of Mofa settings that are configurable remotely
    """

    def __init__(self):
        self.status = Status.Default
        self.statusType = StatusType.Default
        self.message = ''
        self.settings = FormSettingObjects()

    def parseData(self, data, **attrParseMap):
        """
        Parses/restructures incoming settings data and formats it into a dictionary to be used for adding settings objects to the form. \n
        :data: Nested dictionary of string k,v pairs parsed from the request body. \t
        :type: dict(str, dict(str, str)) \n
        :attrParseMap: Mapping of (casting) functions to use for casting attributes to correct datatypes. \t
        :type: dict(str, func())
        :returns: dictionary containing setting object keys and cast value types \t
        :rtype: dict(str, dict(str, val)) \n
        """
        d = {}
        for entry in data:
            parts = entry.get("name").split('-')  # parts[0] is settingName and parts[1] is the setting's specific attribute
            val = entry.get("value")              # val is the value of the attribute described in parts[1]

            properties = d.get(parts[1])          # the already existing dictionary with other attribute-value pairs of this setting
            parseFunc = attrParseMap.get(parts[1])
            if(parseFunc is not None):  # only if attrParseMap has an entry for the attribute continue parsing
                appendDict = {parts[1]: parseFunc(val)}             # parse the value and create a new k,v pair
                properties = {**d.get(parts[0], {}), **appendDict}  # merge the k,v pair with the existing properties dict of the setting object
                d[parts[0]] = properties
            else:  # if attrParseMap has no entry for the attribute
                d[parts[0]] = d.get(parts[0], {})   # add setting object but ignore attributes
                continue                            # used to later fetch the actual values from the database, if the setting object exists
        return d

    def toJSON(self):
        """
        Structures the form's fields into the final JSON structure to return as the response form \n
        :returns: a JSON formatted dictionary \t
        :rtype: dict \n
        """
        if(self.statusType == StatusType.Update):
            if(self.status == Status.Success):
                self.message = settingStrings.get("updateMessage")
            else:
                self.message = settingStrings.get("updateErrorMessage")
        data = {
            "status": self.status.value,
            "statusType": self.statusType.value,
            "message": self.message,
            "objects": self.settings.generateJSON()
        }

        return data
        # eval(json.dumps(data)) ensures data will adhere to json format,
        # but as the current implementation already returns a dict in json format this is not nessecary


class CourseSettingsForm(StandardForm):
    """
    Form used to represent the current status of a coure's settings \n
    """

    attrParseMap = {"enabled": lambda s: s.lower() in ["true"], "value": int}

    def __init__(self, data=None):
        """
        Construct the form, optionally based on a provided JSON formatted string \n
        :data: Optional nested dictionary of string k,v pairs parsed from the request body \t
        :type: dict(str, dict(str, str)) \n
        """
        super(CourseSettingsForm, self).__init__()
        self.settings = CourseSettingObjects()
        if data is not None:
            dataDict = self.parseData(data, **self.attrParseMap)
            for settingName in dataDict.keys():
                st = dataDict[settingName]
                self.settings.add(settingName, st.get('enabled'), st.get('value'))

    def addObject(self, settingName, mode, value):
        """
        Wrapper function for adding a settings object to the form, ensures correct types for the object's values. \n
        :settingName: key of the setting object to add \t
        :type: str \n
        :mode: toggle of the course setting \t
        :type: bool \n
        :value: value for the course setting \t
        :type: int \n
        """
        if(isinstance(mode, bool) and isinstance(value, int)):
            self.settings.add(settingName, mode, value)

    def updateObject(self, settingName, mode, value):
        """
        Wrapper function for updating the form's settings objects values. \n
        :settingName: key of the settings object to modify \t
        :type: str \n
        :mode: toggle of the course setting \t
        :type: bool \n
        :value: value for the course setting \t
        :type: int \n
        """
        if(isinstance(mode, bool) and isinstance(value, int)):
            obj = self.settings.get(settingName)
            if(obj is not None):
                self.settings.add(settingName, mode, value)
            else:
                return


class AssistantSettingsForm(StandardForm):
    """
    Form used to represent the status of the course's current assistants
    """

    def __strToDbAction(action):
        """
        Converts the dbAction string to its Enum type.
        """
        if (action == 'add'):
            return DbAction.Add
        elif (action == 'update'):
            return DbAction.Update
        elif (action == 'remove'):
            return DbAction.Remove
        else:
            return None

    attrParseMap = {"dbAction": __strToDbAction, "quizId": int, "score_threshold": int}

    def __init__(self, data=None):
        """
        Construct the form, optionally based on a provided JSON formatted string \n
        :data: Optional nested dictionary of string k,v pairs parsed from the request body \t
        :type: dict(str, dict(str, str)) \n
        """
        super(AssistantSettingsForm, self).__init__()
        self.settings = AssistantSettingObjects()
        if data is not None:
            dataDict = self.parseData(data, **self.attrParseMap)
            for assistantName in dataDict.keys():
                try:
                    key = AssistantKey(assistantName)   # cast assistant string to its corresponding key
                except ve_exc:
                    key = AssistantKey.Unknown          # cast any mismatching/unknown strings to 'unknown' key
                self.addObject(key, **dataDict[assistantName])

    def addObject(self, assistantName, **kwargs):
        """
        Wrapper function for adding a settings object to the form, ensures correct types for the object's values. \n
        :settingName: key of the assistant setting object to add \t
        :type: str \n
        :kwargs: dictionary providing the assistant's attribute values \t
        :type: dict \n
        """
        self.settings.add(assistantName, **kwargs)

    def updateObject(self, assistantName, **kwargs):
        """
        Update the assistant settings object based on k,v pairs representing its attributes and values. \n
        :settingName: key of the assistant setting object to add \t
        :type: str \n
        :kwargs: dictionary providing the assistant's attribute values \t
        :type: dict \n
        """
        obj = self.settings.get(assistantName)
        if(obj is not None):
            self.settings.add(assistantName, **kwargs)
        else:
            return
