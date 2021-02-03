# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

from analytics.src import lrsConnect as lrs
from analytics.src import utils

from django.conf import settings


def countViewedStatements(courseid):
    """
    Count the amount of 'viewed' statements from a specific course \n
    :type courseid: str \n
    :returns: The amount of statements in a dictionary with 'count' as the only key \n
    :rtype: dict<string:int> \n
    """
    statements = getViewHistory(courseid)
    if utils.hasError(statements):
        return statements
    return {"count": len(statements)}


def generateViewedHistory(courseid):
    """
    Count the amount of 'viewed' statements from a specific course per activity per date \n
    :type courseid: str \n
    :returns: A dictionary of pages with for each page a list of dictionaries containing the date and the count \n
    :rtype: dict<string:list<dict<string,mixed>>> \n
    """
    data = getViewHistory(courseid)
    if utils.hasError(data):
        return data

    # Group the statements by activity (emodule)
    pages = utils.groupOn(
        data,
        lambda x: x["activity"],
        lambda x: [utils.getDate(x["timestamp"])],
        lambda total, x: total + [utils.getDate(x["timestamp"])]
    )

    # For each emodule, group by date and count the amount of results for each date
    pages = utils.mapDict(
        pages,
        lambda lst: utils.dictAsKvParray(
            utils.groupOn(
                lst,
                utils.id,
                lambda x: 1,
                lambda total,
                x: total + 1
            ),
            "date",
            "count"
        )
    )

    return pages


def getViewHistory(courseid):
    """
    Run the query to get the data required for this analysis from the LRS \n
    :type courseid: str \n
    :returns: List of preprocessed statements (dictionaries) from the LRS \n
    :rtype: list<dict<string:mixed>> \n
    """
    return (lrs.Query()
            .select(lrs.Attr.ACTIVITY, lrs.Attr.TIMESTAMP)
            .where(lrs.Attr.VERB, lrs.IS, "http://id.tincanapi.com/verb/viewed")
            .where(lrs.Attr.CONTEXTACTIVITY, lrs.IS, f"{settings.MOODLE_BASE_URL}/course/view.php?id={courseid}")
            .where(lrs.Attr.ACTIVITY, lrs.NOT_IS, f"{settings.MOODLE_BASE_URL}/course/view.php?id={courseid}")
            .where(lrs.Attr.ACTIVITY, lrs.CONTAINS, "view.php?id=")
            .execute()
            )
