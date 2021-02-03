# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

from courses.models import Course


def fetchInactivityParams(courseID):
    """
    Queries the Django database for the course and returns the values of interest.\n
    :courseID: ID of the course \t
    :type: int \n
    :returns: Tuple containing the toggled state and inactivity timelimit.\t
    :rType: (Bool, int)n \n
    """
    obj = Course.objects.get(courseId=int(courseID))
    return (obj.inactivity, obj.inactivity_time)


def updateInactivityParams(courseID, mode, timeLimit):
    """
    Queries the Django database for the course and updates the inactivity according to the given arguments.\n
    :courseID: ID of the course \t
    :type: int \n
    :mode: mode of operation: True == active, False == inactive\t
    :type: bool \t
    :timeLimit: Time interval in days after which to start messaging student about inactivity \n
    :type: int \t
    """
    obj = Course.objects.get(courseId=int(courseID))
    if(mode is not None):   # value will be None if it does not require an update
        obj.inactivity = mode
    if(timeLimit is not None):   # value will be None if it does not require an update
        obj.inactivity_time = timeLimit
    obj.save()
