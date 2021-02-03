# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

import json

from courses.models import Course, Quiz
from assistants.models import QuizCompletedFeedback


def getAllQuizAssistants(courseID):
    """
    Get all Quiz Assistants registered to the course
    :courseID: Moodle ID for the course in which the quiz is located. \t
    :type: str \n
    :returns: list of assistant attributes relevant for remote configuration. \t
    :rtype: list<dict<k,v>>\n
    """
    raise NotImplementedError()


def getQuizAssistant(courseID, quizID):
    """
    Get the single quiz Assistant registered to the quizId from a course
    :courseID: Moodle ID for the course in which the quiz is located. \t
    :type: str \n
    :courseID: Moodle ID for the quiz to which the assistant is bound. \t
    :type: str \n
    """
    raise NotImplementedError()


def createQuizAssistant(courseID, quizID, scoreThresh):
    """
    Adds a new quiz assistant to the mofa database. \n
    :courseID: Moodle ID for the course in which the quiz is located. \t
    :type: str \n
    :quizID: Moodle ID for the quiz to add the assistant to.\t
    :type: str \n
    :scoreThresh: Score threshold for the assistant to send feedback to students. \t
    :type: int \n
    :returns: a Json formatted string indicating success of the operation\t
    :rtype: str \n
    """
    raise NotImplementedError()


def updateQuizAssistant(courseID, quizID, scoreThresh, toggle):
    """
    Adds a new quiz assistant to the mofa database. \n
    :courseID: Moodle ID for the course in which the quiz is located. \t
    :type: str \n
    :quizID: Moodle ID for the quiz to add the assistant to.\t
    :type: str \n
    :scoreThresh: Score threshold for the assistant to send feedback to students. \t
    :type: int \n
    :toggle: toggle if the assistant will actively provide feedback to the course's students. \t
    :type: bool \n
    :returns: a Json formatted string indicating success of the operation\t
    :rtype: str \n
    """
    raise NotImplementedError()


def deleteQuizAssistant(courseID, assistantID):
    """
    Removes the quiz assistant based on the provided ID \n
    :courseID: Moodle ID for the course to which the assistand is related. \t
    :type: str \n
    :assistantID: Mofa ID for the quiz assitant to delete.\t
    :type: str \n
    :returns: a Json formatted string indicating success of the operation\t
    :rtype: str \n
    """
    raise NotImplementedError()
