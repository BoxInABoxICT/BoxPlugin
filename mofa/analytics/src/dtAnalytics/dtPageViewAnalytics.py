# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
from analytics.src import utils
from analytics.src import lrsConnect as lrs

from datetime import datetime, timedelta

from django.conf import settings

from copy import deepcopy

import numpy as np
import pandas as pd
from sklearn import linear_model
import math

import os
import json


def dtViewedPages(scenarioID, courseid):
    """
    Calculates the optimal regression model and returns the coefficients of the pages.
    \n
    :param scenarioID: The id of the scenario to calculate the correlation for \t
    :type scenarioID: string \n
    :param courseid: The course to correlate the scenario with. \t
    :type courseid: string \n
    :returns: A dictionary with the coefficients and some metadata \t
    :rtype: dict \n
    """
    d = os.path.dirname(os.path.realpath(__file__))
    if (not os.path.isfile(f"{d}/response_{scenarioID}_{courseid}.json")):
        getStudentData(scenarioID, courseid)
        return dtViewedPages(scenarioID, courseid)

    studentdata = loadStudentData(scenarioID, courseid)

    if utils.hasError(studentdata):
        return studentdata

    featuredata = getFeatures(studentdata)
    features = featuredata["features"]
    scores = featuredata["scores"]

    options = [0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]

    resultOptions = list(map(lambda percentage: linearRegression(features, scores, percentage), options))

    best = resultOptions[0]
    for result in resultOptions:
        if result["predRMSE"] < best["predRMSE"]:
            best = result

    return best


def linearRegression(features, scores, trainpercentage=0.6):
    """
    Create a Ridge linear regression model and return the RMSE and the pageCoefficients
    \n
    :param features: The dictionary of features to use \t
    :type features: dict \n
    :param scores: A list of the correct scores for the dictionary features \t
    :type scores: list \n
    :param trainpercentage: The percentage of data to use for training. The other part will be used for testing \t
    :type trainpercentage: float \n
    :returns: A dictionary with the data \t
    :rtype: dict \n
    """
    df = pd.DataFrame(features)
    traincount = round(trainpercentage * len(df))

    df_train = df[:traincount]
    score_train = scores[:traincount]
    df_test = df[traincount:]
    score_test = scores[traincount:]

    reg = linear_model.Ridge(alpha=2.0)
    reg.fit(df_train, score_train)

    pageCoefs = list(map(lambda page, coef: {"page": page, "coef": round(coef)}, features.keys(), reg.coef_))

    medians = [utils.getMedian(score_test)] * len(score_test)
    pred = reg.predict(df_test)

    medianRMSE = getRMSE(medians, score_test)
    predRMSE = getRMSE(pred, score_test)

    return {
        "trainingPercentage": trainpercentage * 100,
        "intercept": reg.intercept_,
        "medianRMSE": medianRMSE,
        "predRMSE": predRMSE,
        "pageCoefs": pageCoefs
    }


def getRMSE(set1, set2):
    """
    Gets the Root Mean Squared Error of two same length sets.
    \n
    :param set1: The first set \t
    :type set1: iterable \n
    :param set2: A second set with the same length as set1 \t
    :type set2: iterable \n
    :returns: The Root Mean Squared Error \t
    :rtype: float \n
    """
    if (len(set1) == 0 or len(set2) == 0):
        return 0
    sqe = list(map(lambda a, b: (a - b) * (a - b), set1, set2))
    return math.sqrt(sum(sqe) / len(sqe))


def getStudentData(scenarioID, courseid):
    """
    Collect the ids and timestamps of the students that completed a scenario and for each student, get the pages they looked at in the 14 days before that.
    \n
    :param scenarioID: The scenario to perform the analysis on \t
    :type scenarioID: string \n
    :param courseid: The courseid of the course the scenario belongs to \t
    :type courseid: string \n
    :returns: void \t
    :rtype: void \n
    """
    data = getDTdata(scenarioID)
    studentdata = ""
    if utils.hasError(data):
        studentdata = data
    else:
        aggregated = groupByStudent(data)
        studentdata = list(map(lambda data, actor: {"score": data["score"], "pages": getPageViewData(courseid, actor, data["timestamp"])}, list(aggregated.values()), list(aggregated.keys())))
    d = os.path.dirname(os.path.realpath(__file__))
    f = open(f"{d}/response_{scenarioID}_{courseid}.json", "w")
    f.write(json.dumps(studentdata))
    f.close()


def loadStudentData(scenarioID, courseid):
    """
    Load the response file of one analysis
    \n
    :param scenarioID: The scenarioID to load the response file for \t
    :type scenarioID: string \n
    :param courseid: The courseid of the course to load the response file for \t
    :type courseid: string \n
    :returns: A json structured dictionary \t
    :rtype: dict \n
    """
    d = os.path.dirname(os.path.realpath(__file__))
    f = open(f'{d}/response_{scenarioID}_{courseid}.json')
    data = json.load(f)
    return data


def getFeatures(studentdata):
    """
    From a set of studentdata, extract and filter the features.
    \n
    :param studentdata: A set of student data (in the format of the response files) to extract features from \t
    :rtype studentdata: dict \n
    :returns: A dictionary of features \t
    :rtype: dict \n
    """
    uniquepages = [a for b in list(map(lambda stm: stm["pages"], deepcopy(studentdata))) for a in b]
    uniquepages = list(set(uniquepages))
    featuredata = extractFeatures(uniquepages, studentdata)

    studentVisitTreshold = 0.05  # at leas 5% of students needs to visit the page
    studentcount = len(studentdata)

    featuredata["features"] = {k: v for k, v in featuredata["features"].items() if len(list(filter(lambda x: x > 0, v))) >= studentVisitTreshold * studentcount}

    rejected = len(uniquepages) - len(featuredata["features"])

    return featuredata


def extractFeatures(pages, dataset):
    """
    Extract the amount of page views for each student for each page
    \n
    :param pages: A list of all the (unique) pages to use \t
    :type pages: list \n
    :param dataset: A list of dictionaries, each dictionary representing one student and having at least the key "pages" \t
    :type dataset: [dict] \n
    :returns: A dictionary with two keys: "scores" and "features" \t
    :rtype: dict \n
    """
    scores = list()
    pageslists = dict()
    for page in pages:
        pageslists[page] = list()

    for datapoint in dataset:
        scores.append(datapoint.get("score"))
        for page in pages:
            if page in datapoint["pages"]:
                pageslists[page].append(datapoint["pages"][page])
            else:
                pageslists[page].append(0)

    return {"scores": scores, "features": pageslists}


def getPageViewData(courseid, actorid, untiltime):
    """
    For one student, get all the pages viewed between the untiltime and 14 days earlier
    \n
    :param courseid: The course to which the pages should belong \t
    :type courseid: string \n
    :param actorid: The full LRS id of the student to get the page views for \t
    :type actorid: string (stringified json) \n
    :param untiltime: A "YYYY-MM-DDThh:mm:ssZ" formatted timestamp \t
    :type untiltime: string (datetime) \n
    :returns: A dictionary of pages visited pages and for each page the amount of visits \t
    :rtype: dict \n
    """
    def stmInRange(lower, upper, stm):
        timestamp = datetime.fromisoformat(stm["timestamp"].replace(".000Z", ""))
        return lower < timestamp and timestamp < upper

    untiltime = datetime.fromisoformat(untiltime.replace("Z", ""))
    sincetime = untiltime - timedelta(days=14)
    querydata = (
        lrs.Query()
        .select(lrs.Attr.ACTIVITY, lrs.Attr.TIMESTAMP)
        .where(lrs.Attr.VERB, lrs.IS, "http://id.tincanapi.com/verb/viewed")
        .where(lrs.Attr.CONTEXTACTIVITY, lrs.IS, f"http://localhost/course/view.php?id={courseid}")
        .where(lrs.Attr.ACTIVITY, lrs.CONTAINS, "/mod/page/view.php")
        .where(lrs.Attr.ACTOR, lrs.IS, actorid)
        .execute()
    )
    querydata = filter(lambda stm: stmInRange(sincetime, untiltime, stm), querydata)
    querydata = map(lambda stm: utils.getIdFromUrl(stm["activity"]), querydata)
    querydata = utils.groupOn(querydata, utils.id, lambda x: 1, lambda total, x: total + 1)

    return querydata


def getDTdata(scenarioID):
    """
    Query the LRS for all the students that completed a specific scenario
    \n
    :param scenarioID: The id of the scenario that was completed \t
    :type scenarioID: string \n
    :returns: A list of scenario completions (xAPI statements), with for each completion the timestamp, the actor and the result \t
    :rtype: [dict] \n
    """
    return (
        lrs.Query()
        .where(lrs.Attr.ACTIVITY, lrs.IS, f"https://en.dialoguetrainer.app/scenario/play/{scenarioID}")
        .where(lrs.Attr.VERB, lrs.IS, "https://adlnet.gov/expapi/verbs/completed")
        .select(lrs.Attr.ACTOR, lrs.Attr.RESULT, lrs.Attr.TIMESTAMP)
        .execute()
    )


def groupByStudent(dataset):
    """
    Calculate the total score of each scenario for each student and group the scenario completions by student
    \n
    :param dataset: A list of xAPI statements, each containing at least the actor, the timestamp and the result \t
    :type dataset: [dict] \n
    :returs: A dictionary, with for each student the score and timestamp of their first attempt \t
    :rtype: dict<float> \n
    """
    newDataset = utils.groupOn(
        dataset,
        lambda x: x["actor"],
        lambda x: {"timestamp": x["timestamp"], "score": utils.getAverageScore(x["result"])},
        # lambda total, x: {"timestamp": x["timestamp"], "score": getAverageScore(x["result"])} if getAverageScore(x["result"]) > total["score"] else total
        lambda total, x: {"timestamp": x["timestamp"], "score": utils.getAverageScore(x["result"])}
    )
    return newDataset
