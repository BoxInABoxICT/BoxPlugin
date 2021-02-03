# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

import json
import math
from urllib.parse import urlparse, parse_qs


def getDate(timestamp):
    """
    Extracts the date from a timestamp.
    :param timestamp: The timestamp from which the date should be obtained. \t
    :type timestamp: string \n
    :returns: The date info of the timestamp. \t
    :rtype: string \n
    """
    return timestamp.split('T')[0]


def dictAsKvParray(data, keyName, valueName):
    """
    Transforms the contents of a dictionary into a list of key-value tuples.
    For the key-value tuples chosen names for the keys and the values will be used.
    :param data: The dictionary from which the date should be obtained. \t
    :type data: Dict<mixed, mixed> \n
    :param keyName: The name assigned to the key of the tuples. \t
    :type keyName: string \n
    :param valueName: The name assigned to the value of the tuples \t
    :type valueName: string \n
    :returns: A list of key-value tuples with the chosen names for the keys and values.  \t
    :rtype: [{keyName: mixed, valueName: mixed}] \n
    """
    res = []
    for key in data.keys():
        res.append({keyName: key, valueName: data[key]})
    return res


def mapDict(dictionary, func):
    """
    Applies a function to the values of a dictionary.
    :param dictionary: The dictionary for which a function should be applied on the values of its tuples. \t
    :type dictionary: Dict<mixed, mixed> \n
    :param func: The function to be applied on the value of a tuple. \t
    :type func: function \n
    :returns: A dictionary with func applied to all the values of its tuples.  \t
    :rtype: : Dict<mixed, mixed> \n
    """
    return {k: func(v) for k, v in dictionary.items()}


def groupOn(array, keyFunc, initFunc, aggregateFunc):
    """
    Apply a function on each element of array and put them in a dictionary:
    If the element function is not a key yet in the dictionary, apply another function to it and assign that as the value in the dictionary.
    If the element function is already a key, apply an aggregrate function on the current value of it and the duplicate key.
    :param array: The array which contents will put into the resulting dictionary. \t
    :type array: [mixed] \n
    :param keyFunc: The function to be applied on the elements of the array. This will be used as the key of the dictionary. \t
    :type keyFunc: function \n
    :param initFunc: The function to be applied on non-duplicate elements of the array/dictionary. This will be used as the initial value of the dictionary. \t
    :type initFunc: function \n
    :param aggregateFunc: The aggregate function to be applied on duplicate elements of the array/dictionary. This will be used to aggregrate the value of the dictionary. \t
    :type aggregateFunc: function \n
    :returns: A non-duplicate dictionary with the different functions applied to its keys and values.  \t
    :rtype: : Dict<mixed, mixed> \n
    """
    result = dict()
    for elem in array:
        key = keyFunc(elem)
        if key not in result:
            result[key] = initFunc(elem)
        else:
            result[key] = aggregateFunc(result[key], elem)
    return result


def any(array, mapFunc):
    """
    Checks if any of the elements of array returns true, when applied on a function that returns a boolean.
    :param array: The array that will be checked, for if any of the elements returns true, when applied on the function. \t
    :type array: [mixed] \n
    :param mapFunc: The function that gives a boolean value, when applied on the element of the array. \t
    :type mapFunc: function \n
    :returns: Whether any of the elements of the array, returned true or not.  \t
    :rtype: : bool \n
    """
    for elem in array:
        if mapFunc(elem):
            return True
    return False


def id(arg):
    """
    Returns the given argument unchanged.
    :param arg: The element that must be returned unchanged. \t
    :type arg: mixed \n
    :returns: The element that has been given to the function.  \t
    :rtype: : mixed \n
    """
    return arg


def hasError(data):
    """
    Checks whether or not a string "error" is in the given argument.
    :param data: The element that must be checked for if it contains the string "error". \t
    :type data: mixed \n
    :returns: True of false depending on if the "error" was in the given argument.  \t
    :rtype: : bool \n
    """
    return "error" in data


def transposeLists(lists):
    """
    Reorders all the elements of a multidimensionsional list, by putting all the nth elements of the inner dimensions into the inner dimensional lists.
    As example, if the first elements of the inner dimensions are 1, 2 and 5. An inner list in the result would be a list with 1, 2 and 5 in it.
    :param lists: The multidimensional list to be ordered. \t
    :type lists: [[mixed]] \n
    :returns: A reordered multidimensional list based on the inner indexes of the input argument "lists".  \t
    :rtype: : [[mixed]] \n
    """
    lists = list(lists)
    cols = []
    while (len(lists) > 0):
        col = map(lambda lst: lst[0], lists)
        cols.append(list(col))

        lists = filter(lambda lst: len(lst) > 1, lists)
        lists = map(lambda lst: lst[1:], lists)
        lists = list(lists)
    return cols


def getSetStatistics(lst):
    """
    Returns a dictionary with the count, average, min, max, quartiles, median and standard deviation of a set of numbers.
    :param lst: A list of numerics on which analytics will be applied. \t
    :type lst: [numerics] \n
    :returns: A dictionary of the count, average, min, max, quartiles, median and standard deviation.  \t
    :rtype: : Dict<string, int> \n
    """
    lst = list(lst)
    count = len(lst)
    total = sum(lst)
    avg = total / count

    lowest = min(lst)
    highest = max(lst)

    sd = math.sqrt(sum(map(lambda num: pow(num - avg, 2), lst)) / count)

    return {
        "count": count,
        "average": round(avg),
        "min": round(lowest),
        "max": round(highest),
        "q1": round(getQ1(lst)),
        "median": round(getMedian(lst)),
        "q3": round(getQ3(lst)),
        "standarddeviation": round(sd)
    }


def getMedian(lst):
    """
    Returns the median of a list of numerics.
    :param lst: A list of numerics from which the median will be retrieved. \t
    :type lst: [numerics] \n
    :returns: The median.  \t
    :rtype: : Numeric \n
    """
    lstSort = sorted(lst)
    medianPoints = getMedianpoints(lstSort)
    return getMedianvalue(lstSort, medianPoints)


def getQ1(lst):
    """
    Returns the first quartile of a list of numerics.
    :param lst: A list of numerics from which the first quartile will be retrieved. \t
    :type lst: [numerics] \n
    :returns: The first quartile.  \t
    :rtype: : Numeric \n
    """
    lstSort = sorted(lst)
    medianPoints = getMedianpoints(lstSort)
    if medianPoints[1] == -1:
        bound = int(medianPoints[0])
    else:
        bound = int(medianPoints[1])
    q1List = lstSort[:bound]
    quartilePoints = getMedianpoints(q1List)
    return getMedianvalue(q1List, quartilePoints)


def getQ3(lst):
    """
    Returns the third quartile of a list of numerics.
    :param lst: A list of numerics from which the third quartile will be retrieved. \t
    :type lst: [numerics] \n
    :returns: The third quartile.  \t
    :rtype: : Numeric \n
    """
    lstSort = sorted(lst)
    medianPoints = getMedianpoints(lstSort)
    if medianPoints[1] == -1:
        if len(lstSort) == 1:
            bound = 0
        else:
            bound = int(medianPoints[0] + 1)
    else:
        bound = int(medianPoints[1])
    q3List = lstSort[bound:]
    quartilePoints = getMedianpoints(q3List)
    return getMedianvalue(q3List, quartilePoints)


def getMedianpoints(lst):
    """
    Returns the index or indexes of the median of a list of numerics.
    :param lst: A list of numerics from which the median index or indexes will be retrieved. \t
    :type lst: [numerics] \n
    :returns: The median index or indexes.  \t
    :rtype: : (int, int) \n
    """
    count = len(lst)
    if count == 1:
        return (1, -1)
    elif count % 2 == 1:
        return (int((count - 1) / 2), -1)
    else:
        return (int((count / 2) - 1), int(count / 2))


def getMedianvalue(lst, points):
    """
    Returns the median of a list of numerics.
    :param lst: A list of numerics from which the median will be retrieved. \t
    :type lst: [numerics] \n
    :returns: The median.  \t
    :rtype: : Numeric \n
    """
    if points[1] == -1:
        if len(lst) == 1:
            return lst[0]
        else:
            medianIndex = points[0]
            return lst[points[0]]
    else:
        medianLeftIndex = points[0]
        medianRightIndex = points[1]
        return (lst[medianLeftIndex] + lst[medianRightIndex]) / 2


def getSequenceDifference(lst):
    """
    Returns an array of the subtracted value from each nth + 1 element and the nth element.
    :param lst: A list of numerics from which the differences between following elements will be retrieved. \t
    :type lst: [numerics] \n
    :returns: The subtracted values from each nth + 1 element and the nth element.  \t
    :rtype: : [numerics] \n
    """
    return [a - b for a, b in zip(lst[1:], lst[:-1])]


def getIdFromUrl(url):
    """
    Get the id parameter from a url
    \n
    :param url: The url with the id parameter in it \t
    :type url: string \n
    :returns: The parameter value from the url \t
    :rtype: mixed \n
    """
    return parse_qs(urlparse(url).query)['id'][0]


def getAverageScore(result):
    """
    Get the average score of a set of subscores for a student
    \n
    :param result: A dicitonary containing the results of a student \t
    :type result: {extensions : {http://www.boxinabox.nl/extensions/multiple-results : [{value, ...}], ...}, ...} \n
    :returns: The average score \t
    :rtype: double \n
    """
    extensions = result["extensions"]["http://www.boxinabox.nl/extensions/multiple-results"]
    extensions = extensions.values()
    extensions = [elem for elem in list(extensions) if isinstance(elem["value"], int)]
    extensions = map(lambda res: res["value"], extensions)
    extensions = list(extensions)
    if (len(extensions) == 0):
        return 0
    return sum(extensions) / len(extensions)
