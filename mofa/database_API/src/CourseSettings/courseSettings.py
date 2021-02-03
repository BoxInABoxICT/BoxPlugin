# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

from enum import Enum
from database_API.src.configForms import *

from database_API.src.CourseSettings.deadline_db_update import *
from database_API.src.CourseSettings.inactivity_db_update import *


class SettingKeys(Enum):
    """
    Enum class representing the different course settings that are an attribute of the Course model
    """
    Deadline = 'deadline'
    Inactivity = 'inactivity'


def fetchCourseSettings(courseID, form):
    """
    Add all course setting objects to the form by querying the database for each one. \n
    :courseID: Moodle ID for the course in which the quiz is located. \t
    :type: str \n
    :form: The courseSettings form to be returned in the http response. \n
    :type: CourseSettingsForm
    """
    form.statusType = StatusType.Fetch
    for obj in SettingKeys:
        fetchSwitch(courseID, obj, form)
    if(form.status != Status.Error):
        form.status = Status.Success


def updateCourseSettings(courseID, form):
    """
    Iterate through each given settingsObject to update the current db parameters for the form's setting objects \n
    :courseID: Moodle ID for the course in which the quiz is located. \t
    :type: str \n
    :form: The courseSettings form to be returned in the http response. \n
    :type: CourseSettingsForm
    """
    form.statusType = StatusType.Update
    for objkey in SettingKeys:
        updateSwitch(courseID, objkey, form)
    if(form.status != Status.Error):
        form.status = Status.Success


def fetchSwitch(courseID, key, form):
    """
    Fetches the coursesettings and adds these to the form. \n
    :courseID: Moodle ID for the course in which the quiz is located. \t
    :type: str \n
    :key: type of course setting to fetch \t
    :type: SettingKey \n
    :form: The courseSettings form to be returned in the http response. \n
    :type: CourseSettingsForm
    """
    if(key == SettingKeys.Deadline):
        (toggle, value) = fetchDeadlineParams(courseID)
        form.addObject(SettingKeys.Deadline.value, toggle, value)
    elif(key == SettingKeys.Inactivity):
        (toggle, value) = fetchInactivityParams(courseID)
        form.addObject(SettingKeys.Inactivity.value, toggle, value)
    form.status = Status.Success
    return


def updateSwitch(courseID, key, form):
    """
    Updates the coursesettings and adds the updated values to the form. \n
    :courseID: Moodle ID for the course in which the quiz is located. \t
    :type: str \n
    :key: type of course setting to update \t
    :type: SettingKey \n
    :form: The courseSettings form to be returned in the http response. \n
    :type: CourseSettingsForm
    """
    form.statusType = StatusType.Update
    if(key == SettingKeys.Deadline):
        settings = form.settings.get(key.value)
        if settings is not None:
            updateDeadlineParams(courseID, settings[0], settings[1])
        (toggle, value) = fetchDeadlineParams(courseID)
        if settings is not None:
            form.updateObject(key.value, toggle, value)
        else:
            form.addObject(key.value, toggle, value)
    elif(key == SettingKeys.Inactivity):
        settings = form.settings.get(key.value)
        if settings is not None:
            updateInactivityParams(courseID, settings[0], settings[1])
        (toggle, value) = fetchInactivityParams(courseID)
        if settings is not None:
            form.updateObject(key.value, toggle, value)
        else:
            form.addObject(key.value, toggle, value)
    else:
        form.status = Status.Error
        return

    form.status = Status.Success
    return
