# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import json

from assistants.learning_locker import LearningLockerException

from analytics.src import utils
from analytics.src import lrsConnect as lrs

from django.conf import settings


def generateData(courseid):
    """
    Generate the data for the quiz participation analysis \n
    :type courseid: str \n
    :returns: dictionary containing the completion percentage for each quiz \n
    :rtype: dict<str,double> \n
    """
    data = runQuery(courseid)
    if utils.hasError(data):
        return data

    # The 'activity' of submitting a quiz is an 'attempt'. This mapping gets the actual quiz the actor submitted
    quizzes = map(
        lambda stm: {
            "actor": stm["actor"],
            "quiz": list(filter(lambda uri: "/mod/quiz/view.php" in uri, stm["contextActivities"]))[0]
        },
        data
    )

    # Group by the quiz and create a set of all the (distinct) actors that did the quiz
    quizzes = utils.groupOn(
        quizzes,
        lambda x: x["quiz"],
        lambda x: {x["actor"]},
        lambda total, x: total.union({x["actor"]})
    )

    # For each set, the length is the amount of submissions from different actors
    return utils.mapDict(quizzes, len)


def runQuery(courseid):
    """
    Run the query to get the data required for this analysis from the LRS \n
    :type courseid: str \n
    :returns: List of preprocessed statements (dictionaries) from the LRS \n
    :rtype: list<dict<string:mixed>> \n
    """
    return (
        lrs.Query()
        .where(lrs.Attr.CONTEXTACTIVITY, lrs.IS, f"{settings.MOODLE_BASE_URL}/course/view.php?id={courseid}")
        .where(lrs.Attr.VERB, lrs.IS, "http://activitystrea.ms/schema/1.0/receive")
        .where(lrs.Attr.ACTIVITY, lrs.NOT_IS, f"{settings.MOODLE_BASE_URL}/course/view.php?id={courseid}")
        .where(lrs.Attr.CONTEXTACTIVITY, lrs.AnyInSet(lrs.CONTAINS), "/mod/quiz/view.php")
        .select(lrs.Attr.ACTOR, lrs.Attr.CONTEXTACTIVITY)
        .execute()
    )
