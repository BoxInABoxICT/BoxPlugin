# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import json
import re
from datetime import datetime
from datetime import timedelta

from analytics.src import utils
from analytics.src import lrsConnect as lrs
from analytics.src.lrsConnect import LearningLockerException

from django.conf import settings


def analyseModuleVisitTime(courseID):
    """
    Queries the LRS and performs analysis on the time spent by students
    visiting course pages based on a moodle courseID. \n
    :param courseID: Moodle ID of the course to analyse \t
    :type courseID: str \n
    :returns: json formatted data with the following structure [pageID:[(date, durationSum, count)]] \t
    :rtype: json formatted string \n
    """
    # actual analysis happens in these two functions
    queryResult = getStatementData(courseID)
    if(utils.hasError(queryResult)):
        return queryResult      # send data back without any analysis in this case
    data = queryDataToDict(queryResult)
    pageVisitTime = dictionaryActorLoop(data)

    # formatting for response
    result = dict()
    for pageid in pageVisitTime.keys():
        if(pageid == f'{settings.MOODLE_BASE_URL}/course/view.php?id={courseID}'):
            continue

        # cast datetime types to string and group data together as triples
        res = []
        for date in pageVisitTime[pageid].keys():
            datestr = date.strftime('%Y-%m-%d')
            time, count = pageVisitTime[pageid][date]
            res.append({"date": datestr, "time": str(time.total_seconds()), "count": count})

        result[pageid] = res

    return result


def getStatementData(courseID):
    """
    Retrieves and cleans up the xAPI statements from the LRS.
    :param courseID: ID of the course to analyse \t
    :type courseID: str \n
    :param emodID: ID of the emodule of the course to analyse \t
    :type emodID: str \n
    :returns: collection of key value pairs of (userID, timestamp) emodule activity. \t
    :rtype: dict<str,[(Time,str)] \t
    """
    return (lrs.Query()
            .select(lrs.Attr.ACTOR, lrs.Attr.TIMESTAMP, lrs.Attr.ACTIVITY)
            .where(lrs.Attr.CONTEXTACTIVITY, lrs.IS, f"{settings.MOODLE_BASE_URL}/course/view.php?id={courseID}")
            .execute()
            )


def queryDataToDict(data):
    """
    Processes the returned queryresult into a dictionary format usable by the analysis function
    :returns: a dictionary with actor as the key and a tuple with visit timestamp and page ID dict<actorID:[(timestamp, page)] \t
    :rtype: (str, dict<str,[(Time,str)]) \n
    """
    parsedDataDict = {}
    for d in data:
        key = d['actor']
        timeStamp = datetime.strptime(d['timestamp'], '%Y-%m-%dT%H:%M:%S%z')  # cast timestiamp from str to Time
        page = re.match(r'^\S+[.php?id=]([0-9]+)$', d['activity']).group(0)   # regex to capture the page ID
        if key not in parsedDataDict:
            parsedDataDict[key] = []
        parsedDataDict[key].append((timeStamp, page))
    return parsedDataDict


def dictionaryActorLoop(datapoints):
    """
    Loops through the dictionary per actor and runs the sorting and crawling functions on each entry. \n
    :param datapoints: A dictionary with actor as key and an array of timestamps and pageID. \t
    :type datapoints: dict<str,[(Time,str)]> \n
    :returns: double dictionary containing a tuple storing total time spent visiting a page and how many times the page is visited. \t
    :rtype: dict<str:dict<datetime:(timedelta, int)>> \n
    """
    activityHistory = dict()
    for actor in datapoints:
        timestamps = datapoints[actor]
        sortedTimeStamps = sortArray(timestamps)
        if sortedTimeStamps is None:
            continue
        activityHistory = dataCrawler(sortedTimeStamps, activityHistory)
    return activityHistory


def sortArray(timestamps):
    """
    Sorts an array of tuples by timestamp \n
    :param timestamps: An array with tuples of timestamps and pages. \t
    :type timestamps: [(Time,str)] \n
    :returns: Sorted array with tuples. \t
    :rtype:: [(Time,str)] \n
    """
    # Use a lambda function to sort by first element in tuple
    timestamps.sort(key=lambda tuple: tuple[0])
    return timestamps


def dataCrawler(data, activityHistory):
    """
    Traverses trough the data to return a mapping of time spent on a course over time \n
    :param data: tuple of timestamps and pageId indicating the activity history of a single student \t
    :type: [(Time, str)] \n
    :param activityHistory: nested dictionary with the following (key) structure: dict<pageID, dict<date, (duration sum, number of valid visits)>> \t
    :type dict<str, dict<str, (TimeInterval, int)>>: str \n
    :returns: TODO of visit durations \t
    """
    min_time = timedelta(seconds=5)     # TODO: assign through config, testing is based on these values
    max_time = timedelta(hours=1)       # TODO: assign through config, would recommend keeping them unchanged/defaulting to these vals for tests

    for i in range(1, len(data)):       # iterate through the array from second until last element
        duration = data[i][0] - data[i - 1][0]
        # print(f'Page: {data[i-1][1]}, Duration: {duration}')
        if(duration < min_time):        # page is not regarded as visited if too short an interval takes place
            continue
        elif(duration > max_time):      # page is not regarded as visited if too long an interval takes place
            continue
        else:
            entryDate = data[i - 1][0]
            if not data[i - 1][1] in activityHistory:
                activityHistory[data[i - 1][1]] = dict({entryDate.date(): (duration, 1)})
            elif not entryDate.date() in activityHistory[data[i - 1][1]]:
                activityHistory[data[i - 1][1]][entryDate.date()] = (duration, 1)
            else:
                durationSum, visits = activityHistory[data[i - 1][1]][entryDate.date()]
                durationSum += duration
                visits += 1
                activityHistory[data[i - 1][1]][entryDate.date()] = (durationSum, visits)

    return activityHistory
