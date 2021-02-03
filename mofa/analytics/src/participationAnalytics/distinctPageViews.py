# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
from analytics.src import utils
from analytics.src import lrsConnect as lrs

from django.conf import settings


def generateData(courseid):
    """
    Generate the data for the e-module distinct view analysis \n
    :type courseid: str \n
    :returns: dictionary containing the amount of distinct views for each emodule \n
    :rtype: dict<str,int> \n
    """
    data = runQuery(courseid)
    if utils.hasError(data):
        return data

    # Group de data on activity and create a set of distinct actors for each activity
    pages = utils.groupOn(
        data,
        lambda x: x["activity"],
        lambda x: {x["actor"]},
        lambda total, x: total.union({x["actor"]})
    )

    # The length of the set of actors is the amount of views from different actors
    return utils.mapDict(pages, len)


def runQuery(courseid):
    """
    Run the query to get the data required for this analysis from the LRS \n
    :type courseid: str \n
    :returns: List of preprocessed statements (dictionaries) from the LRS \n
    :rtype: list<dict<string:mixed>> \n
    """
    return (
        lrs.Query()
        .select(lrs.Attr.ACTIVITY, lrs.Attr.ACTOR)
        .where(lrs.Attr.CONTEXTACTIVITY, lrs.IS, f"{settings.MOODLE_BASE_URL}/course/view.php?id={courseid}")
        .where(lrs.Attr.ACTIVITY, lrs.NOT_IS, f"{settings.MOODLE_BASE_URL}/course/view.php?id={courseid}")
        .where(lrs.Attr.VERB, lrs.IS, "http://id.tincanapi.com/verb/viewed")
        .where(lrs.Attr.ACTIVITY, lrs.CONTAINS, "view.php")
        .execute()
    )
