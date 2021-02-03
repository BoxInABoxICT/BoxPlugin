# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import json

from assistants.learning_locker import connect
from assistants.learning_locker import LearningLockerException


def getLrsData(table, query):
    """
    Wrapper function to query the lrs through table and query arguments without string formatting \n
    :param table: The table to query from \t
    :type table: string \n
    :param query: The query to send to the LRS \t
    :type query: string \n
    :returns: An HTTP response \t
    :rtype: object \n
    """
    return lrsRequest(f'/data/xAPI/{table}?{query}')


def lrsRequest(queryurl):
    """
    Sends a HTTP GET request to LRS with the specified URL \n
    :param queryurl: The url to send to the LRS \t
    :type queryurl: string \n
    :returns: An HTTP response \t
    :rtype: object \n
    """
    content = 'application/json'
    xApiVersion = '1.0.3'
    headers = {'Content-type': content, 'X-Experience-API-Version': xApiVersion}

    return connect(queryurl, 200, 'get', headers)


def getSimpleLrsData(query):
    """
    Uses a Query object to send the correct queries to the
    LRS and return the correct data from the statements it received. \n
    :param query: The query to execute \t
    :type query: Query \n
    :returns: A list of selected data from statements \t
    :rtype: List \n
    """
    result = []
    more = query.build()
    while(more != '' and more is not None):
        try:
            response = lrsRequest(more)
        except LearningLockerException as lle:
            return {"error": str(lle)}

        body = json.loads(response.text)
        more = str(body['more'])

        result = result + list(query.executeSelect(body["statements"]))
    return result


class Query:
    """
    An object to represent an xAPI query
    """

    def __init__(self):
        """
        Create a new query and set the format constraint by default to 'ids'
        """
        self.params = dict()
        self.selects = []
        self.where(Attr.FORMAT, IS, "ids")
        self.filters = []

    def where(self, queryAttr, op, value):
        """
        Add a condition to the statements that are returned \n
        :param queryAttr: The attribute to apply a condition on \t
        :type queryAttr: Attr \n
        :param op: The operator to apply for the condition \t
        :type op: Func(mixed, mixed) -> Bool \n
        :param value: The value to compare the queryattribute to. \t
        :type value: mixed \n
        :returns: Self \t
        :rtype: Query \n
        """
        if "param" in queryAttr and op == IS:
            self.params[queryAttr["param"]] = {"attr": queryAttr, "val": value}
            return self

        if "selector" in queryAttr:
            self.filters.append({"select": queryAttr["selector"], "op": op, "val": value})
        return self

    def build(self):
        """
        Fold the query object into a query URL
        :returns: The query to send to the LRS
        :rtype: string
        """
        query = f"/data/xAPI/statements"

        if len(self.params.keys()) < 1:
            return query

        self.fixConflict(Attr.ACTIVITY, Attr.CONTEXTACTIVITY)
        self.fixConflict(Attr.ACTOR, Attr.CONTEXTACTOR)

        queryparams = ""
        for param in self.params.keys():
            if "bind" not in self.params[param]["attr"]:
                queryparams = queryparams + "&" + param + "=" + self.params[param]["val"]
            else:
                binded = self.params[param]["attr"]["bind"]
                queryparams = queryparams + "&" + param + "=true"
                queryparams = queryparams + "&" + binded["param"] + "=" + self.params[param]["val"]

        query = query + "?" + queryparams[1:]
        return query

    def fixConflict(self, overwrittenAttr, overridingAttr):
        """
        Detect and fix conflicting operators in the query.
        This is required since xAPI can query for some things seperately, but not at the same time in one query. \n
        :param overwrittenAttr: The attribute that is overwritten by the other if present \t
        :type overwrittenAttr: Attr \n
        :param overridingAttr: The attribute that should remain when both are present \t
        :type overridingAttr: Attr \n
        :rtype: Void \n
        """
        if overwrittenAttr["param"] in self.params.keys() and overridingAttr["param"] in self.params.keys():
            value = self.params[overwrittenAttr["param"]]["val"]
            self.filters.append({"select": overwrittenAttr["selector"], "op": IS, "val": value})
            del self.params[overwrittenAttr["param"]]

    def select(self, *selects):
        """
        Add attributes of the statement that should be returned \n
        :param selects: The attributes to select \t
        :type selects: Attr \n
        :returns: Self \t
        :rtype: Query \n
        """
        for select in selects:
            if "key" not in select or "selector" not in select:
                continue
            self.selects.append(select)
        return self

    def selectData(self, statement):
        """
        Apply the select 'filter' on a statement \n
        :param statement: The statement to apply the 'filter' on. \t
        :type statement: json \n
        :returns: The attributes of the statement that are specified in the 'select' \t
        :rtype: Dict \n
        """
        stm = dict()
        for select in self.selects:
            stm[select["key"]] = select["selector"](statement)
        return stm

    def filterData(self, statement):
        """
        Check if a statement meets all the requirements specified in the query conditions \n
        :param statement: The statement to check \t
        :type statement: Dict/json \n
        :returns: True if all requirements are met, False otherwise \t
        :rtype: Bool \n
        """
        return all(map(lambda cond: cond["op"](cond["select"](statement), cond["val"]), self.filters))

    def executeSelect(self, statements):
        """
        Do the post-processing on the statements (not all constraints can be added to the xApi query)
        by first filtering all the statements and then selecting only the required attributes \n
        :param statements: A list of statements \t
        :type statements: [Dict] \n
        :returns: A list of post-processed statements \t
        :rtype: [Dict] \n
        """
        filtered = filter(self.filterData, statements)
        return map(lambda stm: self.selectData(stm), filtered)

    def execute(self):
        """
        Execute the query by running the getSimpleLrsData function. \n
        :returns: The query result \t
        :rtype: [Dict] \n
        """
        return getSimpleLrsData(self)


class Attr:
    """
    All the attributes that are present in an xAPI statement and/or can be used in a query
    """

    # Can be used in 'where' and 'select'
    ACTOR = {
        "key": "actor",
        "selector": lambda stm: json.dumps(stm["actor"]),
        "param": "agent"
    }

    # Can be used in 'where' and 'select'
    VERB = {
        "key": "verb",
        "selector": lambda stm: stm["verb"]["id"],
        "param": "verb"
    }

    # Can be used in 'where' and 'select'
    ACTIVITY = {
        "key": "activity",
        "selector": lambda stm: stm["object"]["id"],
        "param": "activity"
    }

    # Can be used in 'where' and 'select'
    CONTEXTACTIVITY = {
        "key": "contextActivities",
        "selector": lambda stm: list(map(lambda elem: elem["id"], stm["context"]["contextActivities"]["grouping"])),
        "param": "related_activities",
        "bind": ACTIVITY
    }

    # Can be used in 'where'
    FORMAT = {
        "param": "format",
    }

    # Can be used in 'where' and 'select'
    CONTEXTACTOR = {
        "param": "related_agents",
        "bind": ACTOR
    }

    # Can be used in 'where'
    LIMIT = {
        "param": "limit"
    }

    # Can be used in 'where'
    SINCE = {
        "param": "since"
    }

    # Can be used in 'where'
    UNTIL = {
        "param": "until"
    }

    # Can be used in 'where' and 'select'
    TIMESTAMP = {
        "key": "timestamp",
        "selector": lambda stm: stm["timestamp"]
    }

    # Can be used in 'select'
    RESULT = {
        "key": "result",
        "selector": lambda stm: stm["result"]
    }


def AnyInSet(operator):
    """
    Apply an operator to all elements in a set and check if any of them return true
    """
    return lambda elem, val: any(map(lambda item: operator(item, val), elem))


def AllInSet(operator):
    """
    Apply an operator to all elements in a set and check if all of them return true
    """
    return lambda elem, val: all(map(lambda item: operator(item, val), elem))


def IS(attribute, val):
    """
    Check if two values are equal
    """
    return attribute == val


def NOT_IS(attribute, val):
    """
    Check if two values are not equal
    """
    return attribute != val


def IN(attribute, val):
    """
    Check if the value contains the attribute
    """
    return attribute in val


def NOT_IN(attribute, val):
    """
    Check if the value does not contain the attribute
    """
    return attribute not in val


def CONTAINS(attribute, val):
    """
    Check if the attribute contains the value
    """
    return val in attribute


def NOT_CONTAINS(attribute, val):
    """
    Check if the attribute does not contain the value
    """
    return val not in attribute
