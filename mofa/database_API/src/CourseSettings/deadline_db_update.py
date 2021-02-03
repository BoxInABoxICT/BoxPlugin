# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.

from courses.models import Course


def fetchDeadlineParams(courseID):
    """
    Queries the Django database for the course and returns relevant deadline settings.\n
    :courseID: ID of the course \t
    :type: int \n
    :returns: Tuple containing the toggled state and deadline hoursbefore.\t
    :rType: (Bool, int) \n
    """
    obj = Course.objects.get(courseId=courseID)
    return (obj.deadline, obj.hours_before)


def updateDeadlineParams(courseID, mode, hours_before):
    """
    Queries the Django database for the course and updates it with the new variables. \n
    :courseID: ID of the course \t
    :type: int \n
    :mode: mode of operation: True == active, False == inactive \t
    :type: bool \t
    :timeLimit: Hours before the deadline after which to start messaging student about not submitting \n
    :type: int \t
    """
    obj = Course.objects.get(courseId=courseID)
    if(mode is not None):   # value will be None if it does not require an update
        obj.deadline = mode
    if(hours_before is not None):   # value will be None if it does not require an update
        obj.hours_before = hours_before
    obj.save()
