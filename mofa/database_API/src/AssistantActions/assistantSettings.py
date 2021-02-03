# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

from enum import Enum

from database_API.src.configForms import *

from database_API.src.formSettingObjects import AssistantKey, DbAction

from database_API.src.AssistantActions.newActivityActions import *
from database_API.src.AssistantActions.quizCompletedActions import *


def fetchCourseAssistants(courseID, form):
    """
    Add all assistant setting objects to the form by querying the database for each assistant. \n
    :courseID: Moodle ID for the course in which the quiz is located. \t
    :type: str \n
    :form: The assistant settings form to be returned in the http response. \n
    :type: AssistantSettingsForm
    """
    form.statusType = StatusType.Fetch
    for key in AssistantKey:
        fetchSwitch(courseID, key, form)
    if(form.status != Status.Error):  # only indicate succes if no errors have occured
        form.status = Status.Success


def updateAssistants(courseID, form):
    form.statusType = StatusType.Update
    for key in AssistantKey:
        updateSwitch(courseID, key, form)
    if(form.status != Status.Error):  # only indicate succes if no errors have occured
        form.status = Status.Success


def fetchSwitch(courseID, key, form):
    """
    Fetches the assistant settings and adds these to the form. \n
    :courseID: Moodle ID for the course in which the quiz is located. \t
    :type: str \n
    :key: type of assistant setting to fetch \t
    :type: AssistantKey \n
    :form: The  assistant settings form to be returned in the http response. \n
    :type: AssistantSettingsForm
    """
    if(key == AssistantKey.NewActivity):
        assistant = fetchNewActivityAssistant(courseID)
        if(assistant is not None):
            form.addObject(key, **{'dbAction': DbAction.Fetch})
        return
    elif(key == AssistantKey.QuizFeedback):  # not implemented
        assistants = getAllQuizAssistants(courseID)
        if(assistants is not None):
            for assistant in assistants:
                form.addObject(assistantkey, **assistant)
        return
    else:
        return


def updateSwitch(courseID, key, form):
    """
    Updates the assistant settings and adds the updated values to the form. \n
    :courseID: Moodle ID for the course in which the quiz is located. \t
    :type: str \n
    :key: type of assistant setting to update \t
    :type: AssistantKey \n
    :form: The assistant settings form to be returned in the http response. \n
    :type: AssistantSettingsForm
    """
    setting = form.settings.get(key)
    if(key == AssistantKey.NewActivity):
        if(setting is not None):
            action = setting.get('dbAction')
            newActivityActions(courseID, key, action, form)
        else:   # perform fetch if setting is not present in the form yet
            assistant = fetchNewActivityAssistant(courseID)
            if(assistant is not None):
                form.updateObject(key, **{'dbAction': DbAction.Fetch})
        return
    elif(key == AssistantKey.QuizFeedback):  # not implemented
        if(setting is not None):
            for st in setting.values():
                action = st.get('dbAction')
                quizCompletedActions(courseID, key, action, form)
        else:   # perform fetch if setting is not present in the form yet
            getAllQuizAssistants(courseID)
        return
    else:
        return


def newActivityActions(courseID, key, action, form):
    """
    Switch for executing the correct operation on the Assistant. \n
    :key: key of the assistant. \t
    :type: AssistantKey \n
    :action: dbAction to perform. \t
    :type: DbAction \n
    :form: settingsForm containing additional information about (all) assistants \t
    :type: AssistantSettingsForm \n
    """
    result = None
    if(action == DbAction.Add):
        result = createNewActivityAssistant(courseID)
    elif(action == DbAction.Remove):
        result = deleteNewActivityAssistant(courseID)

    if(result is not None):
        form.updateObject(key, **{'dbAction': action})
    else:
        form.updateObject(key, **{'dbAction': DbAction.Error})
        form.status = Status.Error


def quizCompletedActions(courseID, key, action, form):
    """
    Switch for executing the correct operation on the Assistant. \n
    :key: key of the assistant. \t
    :type: AssistantKey \n
    :action: dbAction to perform. \t
    :type: DbAction \n
    :form: settingsForm containing additional information about (all) assistants \t
    :type: AssistantSettingsForm \n
    """
    result = None
    if(action == DbAction.Add):
        result = createQuizAssistant(courseID)  # not implemented
    elif(action == DbAction.Update):
        result = updateQuizAssistant(courseID, key, action, form)  # not implemented
    elif(action == DbAction.Remove):
        result = deleteQuizAssistant(courseID)  # not implemented

    if(result is not None):
        # TODO: synchronize the quiz setting object with returned result from the db
        pass
    else:
        form.settings.update(key, **{'dbAction': DbAction.Error})
        form.status = Status.Error
