# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
from analytics.src import utils
from analytics.src import lrsConnect as lrs

from django.conf import settings


def generateData(courseid):
    """
    Generate the data for the assignment participation analysis \n
    :type courseid: str \n
    :returns: dictionary containing the completion percentage for each assignment \n
    :rtype: dict<str,double> \n
    """
    data = runQuery(courseid)
    if utils.hasError(data):
        return data

    # Group the assignments based on their id (activity) and create a set of distinct actors that completed them
    assignments = utils.groupOn(
        data,
        lambda x: x["activity"],
        lambda x: {x["actor"]},
        lambda total, x: total.union({x["actor"]})
    )

    # The length of each set is the amount of different actors that completed the assignment
    return utils.mapDict(assignments, len)


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
        .where(lrs.Attr.VERB, lrs.IS, "http://activitystrea.ms/schema/1.0/submit")
        .where(lrs.Attr.ACTIVITY, lrs.NOT_IS, f"{settings.MOODLE_BASE_URL}/course/view.php?id={courseid}")
        .where(lrs.Attr.ACTIVITY, lrs.CONTAINS, "/mod/assign/")
        .select(lrs.Attr.ACTIVITY, lrs.Attr.ACTOR)
        .execute()
    )
