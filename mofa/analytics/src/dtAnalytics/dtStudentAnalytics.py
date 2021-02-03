# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
from analytics.src import utils
from analytics.src import lrsConnect as lrs

from django.conf import settings


def betweenStudentsDifference(scenarioID):
    """
    Calculates the statistics for the scores of students within an attempt.
    For example: if there are three students of which one does a scenario once and two of them do it twice,
    the result will be a list of two elements, the first element are the statistics for the first attempt of all three students
    and the second element are the statistics for the two students that did a second attempt.
    \n
    :param scenarioID: The id of the scenario to calculate the statistics for \t
    :type scenarioID: int \n
    :returns: Statistics data with the following structure [{average, min, max, ...}] \t
    :rtype: List<Dict<string, int>> \n
    """
    data = runQuery(scenarioID)
    if utils.hasError(data):
        return data
    attempts = groupByStudent(data)
    attempts = utils.transposeLists(attempts.values())
    attempts = map(utils.getSetStatistics, attempts)
    return list(attempts)


def betweenStudentAttemptDifference(scenarioID):
    """
    Calculates the statistics for the scores of students between each attempt.
    For example, if there are three students of which one does a scenario twice and two of them do it three times,
    the result will be a list of two elements, the first element are the statistics for the improvement between attempt 1 and attempt 2 for all three students
    and the second element are the statistics for the improvement between attempt 2 and 3 for the two students that did a third attempt
    \n
    :param scenarioID: The id of the scenario to calculate the statistics for \t
    :type scenarioID: int \n
    :returns: Statistics data with the following structure [{average, min, max, ...}] | {error} \t
    :rtype: List<Dict<string, int>> | Dict<string, string>\n
    """
    data = runQuery(scenarioID)
    if utils.hasError(data):
        return data
    attempts = groupByStudent(data).values()
    attempts = [utils.getSequenceDifference(lst) for lst in attempts if len(lst) > 1]
    attempts = utils.transposeLists(attempts)
    attempts = map(utils.getSetStatistics, attempts)
    return list(attempts)


def bestAttemptStatistics(scenarioID):
    """
    Calculates the statistics for the best scores of each of the students that completed the scenario.
    For each of the students, the highest score from all their attempts will be selected and for the list of those scores,
    the statistics will be calculated
    \n
    :param scenarioID: The id of the scenario to calculate the statistics for \t
    :type scenarioID: int \n
    :returns: Statistics data with the following structure {average, min, max, ...} | {error} \t
    :rtype: Dict<string, int> | Dict<string, string>\n
    """
    data = runQuery(scenarioID)
    if utils.hasError(data):
        return data
    attempts = groupByStudent(data).values()
    attempts = map(max, attempts)
    return utils.getSetStatistics(attempts)


def groupByStudent(dataset):
    """
    Groups a dataset based on the student id by concatenating the scores of those students into a list
    \n
    :param dataset: A list of dictionaries, each of them containing at least a "actor" and a "result" key \t
    :type dataset: [{actor, result, ...}] \n
    :returns: A dictionary of student id's and the scores they aquired, in the reversed order as the input dataset \t
    :rtype: Dict<string, List<int>> \n
    """
    newDataset = utils.groupOn(
        dataset,
        lambda x: x["actor"],
        lambda x: [utils.getAverageScore(x["result"])],
        lambda total, x: [utils.getAverageScore(x["result"])] + total
    )
    return newDataset


def runQuery(scenarioID):
    """
    Run a query that aquires the data from the lrs for one specific dialoguetrainer scenario
    \n
    :param scenarioID: The id of the scenario to request the data from \t
    :type scenarioID: int \n
    :returns: The data for that scenario or error \t
    :rtype: [Dict<string, mixed>] | {error} \n
    """
    return (
        lrs.Query()
        .where(lrs.Attr.ACTIVITY, lrs.IS, f"https://en.dialoguetrainer.app/scenario/play/{scenarioID}")
        .where(lrs.Attr.VERB, lrs.IS, "https://adlnet.gov/expapi/verbs/completed")
        .select(lrs.Attr.ACTOR, lrs.Attr.RESULT)
        .execute()
    )
