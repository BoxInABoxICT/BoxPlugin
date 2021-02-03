# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Handle deadline related feedback."""
import time
from datetime import datetime, timedelta

import assistants.moodle as moodle_api
from courses.models import Course
from lib import moodle_get_parsers as parser

from scheduler.models import (AssignmentNotificationSent,
                              FirstAssignmentOfCourse)
from scheduler.utils import check_if_ended, get_course_from_db


def get_deadlines_between(assignment_list, start_time, end_time):
    """
    Filter the passed deadlines from the given assignment list.

    :param assignment_list: List of assignments that need to be checked.
    :type assignment_list: list(dict(str,int))
    :param start_time: Time that the deadline needs to have passed.
    :type start_time: int
    :param end_time: Time that the deadline must not have passed yet.
    :type end_time: int
    :return: Dictionary of all the assignments with its passed deadlines.
    :rtype: dict(int, (str, int))
    """
    passed_deadlines = {}
    for assignment in assignment_list:
        assignment_id, due_date, name = parser.parse_single_assignment(assignment)
        if start_time < due_date < end_time:
            passed_deadlines[assignment_id] = (name, due_date)
    return passed_deadlines


def get_assignments(course_id):
    """
    Get all assignments in the course.

    :param course_id: Id of the course that is checked.
    :type course_id: int
    :return: List of assignments.
    :rtype: list(dict(assignment, assignment_content))
    """
    json = moodle_api.get_assignments([course_id])
    return parser.parse_assignment_list(json)


def check_assignment_completion(user_id, assignment_id, course_id):
    """
    Check whether the assignment is completed by a user.

    :param user_id: The user id to check.
    :type user_id: int
    :param assignment_id: The assignment id to check.
    :type assignment_id: int
    :param course_id: Id of the course that is checked.
    :type course_id: int
    :return: Whether the user has completed the assignment or not.
    :rtype: bool
    """
    json = moodle_api.get_assignment_status(course_id, user_id)['statuses']
    assignment_list = [a for a in json if a['cmid'] == assignment_id]
    if len(assignment_list) > 0:
        return assignment_list[0]['state'] != 0


def get_users(course_id):
    """
    Get all users enrolled in a course.

    :param course_id: Id of the course that is checked.
    :type course_id: int
    :return: List of user ids.
    :rtype: list(int)
    """
    users = moodle_api.get_enrolled_users(course_id)
    return parser.parse_enrolled_students(users)


def convert_time(due_date):
    """
    Convert time to the due_date (in seconds) to hours and minutes.

    :param due_date: The due_date in seconds from the beginning of computers (unix-time).
    :type due_date: int
    :return: Hours and seconds until due date.
    :rtype: tuple(int, int)
    """
    remaining_secs = due_date - time.time()
    hours = remaining_secs / 3600
    minutes = (remaining_secs % 3600) / 60
    return int(hours), int(minutes)


def prep_late_warning(assignment_name):
    """
    Create a late warning message.

    :param assignment_name: Name of the assignment.
    :type assignment_name: str
    :return: A late warning message.
    :rtype: str
    """
    return "The deadline for " + assignment_name + " has passed."


def prep_early_warning(hours, minutes, assignment_name):
    """
    Create a early warning message.

    :param hours: Hours until the deadline.
    :type hours: int
    :param minutes: Minutes until the deadline.
    :type minutes: int
    :param assignment_name: Name of the assignment that approaches its deadline.
    :type assignment_name: str
    :return: An early warning message.
    :rtype: str
    """
    return f'The deadline for {assignment_name} is in {hours} hours and {minutes} minutes.'


def send_warnings(message_list):
    """
    Send all users a deadline message.

    :param message_list: List of messages.
    :type message_list: list(tuple(int, str))
    """
    moodle_api.send_bulk_different_messages(message_list)


def register_assignment_notification(assignment_id, notification_type, assignment_deadline):
    """
    Create a database entry informing that the notification for an assignment has been sent

    :param assignment_id: ID of assignment.
    :type assignment_id: int
    :param notification_type: Hardcoded type of notification, defined in scheduler.models.AssignmentNotificationSent
    :type notification_type: string
    :param assignment_deadline: The deadline of the related assignment.
    :type assignment_deadline: datetime.datetime
    """

    assignment_notification = AssignmentNotificationSent(str(assignment_id) + notification_type, assignment_id, notification_type, assignment_deadline)
    assignment_notification.save()


def check_course_assignment_notifications(course_id, scheduler):
    """
    Send all notifications for deadlines that have passed in this course and have not yet had a notification sent.

    :param course_id: Course to check the deadlines for.
    :type course_id: int
    :param scheduler: SchedulerConfig object to call scheduler functions
    :type scheduler: SchedulerConfig
    """

    # Check if the course has passed and thus the notification job should be removed
    if remove_deadline_job_if_course_ended(course_id, scheduler):
        return

    # get the assignment list from moodle
    assignment_list = get_assignments(course_id)
    # Track assignments relevant for update, these are assignments that have yet to sent their notification
    assignments_to_check_on_update = []

    # get the current time, plus a 1 minute buffer
    current_time = datetime.timestamp(datetime.today() + timedelta(minutes=1))

    time_to_deadline = get_time_before_deadline(course_id)
    if time_to_deadline is None:
        print('No time to deadline found in check_course_assignment_notifications for course with id: ' + str(course_id))
    else:
        # get enrolled users
        user_id_list = get_users(course_id)

        # iterate over all assignments
        # send a notification if the deadline has passed or if it's time to send an early notification
        for assignment in assignment_list:
            assignments_to_check_on_update = send_single_assignment_notification(assignment, course_id, current_time, time_to_deadline, user_id_list, assignments_to_check_on_update)

    # update this course again to reschedule itself
    update_first_assignment_notification_time_of_course(course_id, scheduler, assignments_to_check_on_update)


def send_single_assignment_notification(assignment, course_id, current_time, time_to_deadline, user_id_list, assignments_to_check_on_update):
    """
    Send notifications for the deadline of one assignment to all enrolled users. Only send if the deadline has passed and the message has not been sent earlier.

    :param assignment: All information of a single assignment.
    :type assignment: dict(str, str)
    :param course_id: Course ID of course to check the deadlines for.
    :type course_id: int
    :param current_time: timestamp of current time
    :type current_time: int
    :param time_to_deadline: timestamp of time before deadline when early notification should be send ("the deadline will pass soon").
    :type time_to_deadline: int
    :param user_id_list: List of users of course and so of assignment
    :type user_id_list: list(int)
    :param assignments_to_check_on_update: List of assignments that still need messages and thus should be checked when scheduling next message time
    :type assignments_to_check_on_update: [dict(str, str)]
    :return: List of assignments that still need messages and thus should be checked when scheduling next message time
    :rtype: [dict(str, str)]
    """

    assignment_id, due_date, assignment_name = parser.parse_single_assignment(assignment)
    # skip assignments that are older than one day
    if due_date <= datetime.timestamp(get_datetime_of_outdated_assignments()):
        return assignments_to_check_on_update

    # early notification
    send_assignment_notification_early_or_late(True, assignment, assignment_id, due_date, assignment_name, course_id, current_time, time_to_deadline, user_id_list, assignments_to_check_on_update)
    # late notification
    send_assignment_notification_early_or_late(False, assignment, assignment_id, due_date, assignment_name, course_id, current_time, time_to_deadline, user_id_list, assignments_to_check_on_update)

    return assignments_to_check_on_update


def send_assignment_notification_early_or_late(assignment_type_is_early_not_late, assignment, assignment_id, due_date, assignment_name, course_id, current_time, time_to_deadline, user_id_list, assignments_to_check_on_update):
    """
    Sends a 'early' or 'late' notification for the deadline of one assignment to all enrolled users. Only send if the deadline has passed and the message has not been sent earlier.

    :param assignment_type_is_early_not_late: Boolean to give notification type. True is notification type is 'early' else False if 'late'.
    :type assignment_type_is_early_not_late: bool
    :param assignment: All information of a single assignment.
    :type assignment: dict(str, str)
    :param assignmen_id: ID of the assignment
    :type assignmen_id: int
    :param due_date: Timestamp of the assignment's deadline.
    :type due_date: int
    :param assignment_name: Name of the given assignment.
    :type assignment: str
    :param course_id: Course ID of course to check the deadlines for.
    :type course_id: int
    :param current_time: timestamp of current time
    :type current_time: int
    :param time_to_deadline: timestamp of time before deadline when early notification should be send ("the deadline will pass soon").
    :type time_to_deadline: int
    :param user_id_list: List of users of course and so of assignment
    :type user_id_list: list(int)
    :param assignments_to_check_on_update: List of assignments that still need messages and thus should be checked when scheduling next message time
    :type assignments_to_check_on_update: [dict(str, str)]
    """

    # get notification type as a string
    notification_type = 'early' if assignment_type_is_early_not_late else 'late'

    # check if an early notification has already been sent
    check_already_sent = len(AssignmentNotificationSent.objects.filter(assignment_id=assignment_id, notification_type=notification_type)) > 0
    notification_needs_to_be_send = False
    if assignment_type_is_early_not_late:
        notification_needs_to_be_send = due_date > current_time and due_date - time_to_deadline < current_time
    else:
        notification_needs_to_be_send = due_date <= current_time

    # assignment found with an early notification to send, which has not yet been sent
    if not check_already_sent:
        if notification_needs_to_be_send:
            # prep notification
            notify_list = []
            for user_id in user_id_list:
                status = check_assignment_completion(user_id, assignment_id, course_id)
                if not status:
                    message = None
                    # early notification type
                    if assignment_type_is_early_not_late:
                        hours, minutes = convert_time(due_date)
                        if hours >= 0 and minutes > 0:
                            message = prep_early_warning(hours, minutes, assignment_name)
                    # late notification type
                    else:
                        message = prep_late_warning(assignment_name)
                    if message is not None:
                        notify_list.append((user_id, message))
            # sent notification
            if len(notify_list) > 0:
                send_warnings(notify_list)
            # store that notification is sent
            register_assignment_notification(assignment_id, notification_type, datetime.fromtimestamp(due_date))
        elif assignment not in assignments_to_check_on_update and (not assignment_type_is_early_not_late or due_date > current_time):
            assignments_to_check_on_update.append(assignment)


def update_first_assignment_notification_time_of_course(course_id, scheduler, assignments_to_check=None):
    """
    Check if this course's stored first notficiation is still it's actual first notficiation that will need to be send. Else update to the assignment deadline that is earlier.

    :param course_id: The ID of the course to update
    :type course_id: int
    :param scheduler: SchedulerConfig object to reschedule jobs
    :type scheduler: SchedulerConfig
    :param assignments_to_check: list of assignments to check, if None all course assignments of course will be check
    :type assignments_to_check: dict(str, str)
    """

    # Check if the course has passed and thus the notification job should be removed
    if remove_deadline_job_if_course_ended(course_id, scheduler):
        return

    # get or create FirstAssignmentOfCourse to track the next schedule time
    (first_notification_object, newly_created_first_notification) = get_or_create_first_notificaton_object(course_id)

    time_to_deadline = get_time_before_deadline(course_id)
    if time_to_deadline is None:
        print('Error in deadline notification: Course object with id ' + str(course_id) + ' has no time_to_deadline in database. ')
        return

    # init and store the variables
    planned_assignment_id = first_notification_object.assignment_id
    planned_type = first_notification_object.notification_type
    planned_time = None if first_notification_object.time is None else datetime.timestamp(first_notification_object.time)
    if (planned_time is not None and planned_time < datetime.timestamp(datetime.today() - timedelta(minutes=1))) or assignments_to_check is not None:
        planned_time = None
        first_notification_object.time = None

    # get the assignment list from moodle
    assignment_list = get_assignments(course_id) if (assignments_to_check is None) else assignments_to_check

    # check if the first planned notification is up to date
    for assignment in assignment_list:
        (planned_assignment_id, planned_type, planned_time) = update_first_notification_check_single_assignment(assignment, time_to_deadline, planned_assignment_id, planned_type, planned_time)

    # check if the first assignment of this course has been updated
    updated = planned_time is not None and first_notification_object.time != datetime.fromtimestamp(planned_time)

    # if the first deadline notification of this course has been updated, reschedule this course
    if(updated or newly_created_first_notification):
        # save the found variables and update the table
        first_notification_object = update_first_notification_object(first_notification_object, planned_assignment_id, planned_type, planned_time)

    if(updated):
        scheduler.reschedule_job(str(course_id) + 'assignment_check', 'date', {'run_date': datetime.fromtimestamp(planned_time)}, datetime.fromtimestamp(planned_time))


def update_first_notification_check_single_assignment(assignment, time_to_deadline, planned_assignment_id, planned_type, planned_time):
    """
    Check for a single assignment if its deadlines are earlier than the planned deadline. If so, set the new deadline as planned deadline. This planned time will be the earliest that notification will be send for deadlines.

    :param assignment: All information of a single assignment.
    :type assignment: dict(str, str)
    :param time_to_deadline: timestamp of time before deadline when early notification should be send ("the deadline will pass soon").
    :type time_to_deadline: int
    :param planned_assignment_id: ID of assigment
    :type planned_assignment_id: int
    :param planned_type: Type of planned notification ('early' or 'late')
    :type planned_type: str
    :param planned_time: Timestamp of planned time
    :type planned_time: int
    :return: Tuple containing updated values for (planned_assignment_id, planned_type, planned_time)
    :rtype: (int, str, int)
    """

    assignment_id, due_date, assignment_name = parser.parse_single_assignment(assignment)
    # notifications at the planned time can be skipped, notifcations older than one day can also be skipped
    if due_date is planned_time or due_date < datetime.timestamp(datetime.today() - timedelta(days=1)):
        return (planned_assignment_id, planned_type, planned_time)

    # check if an early notification has already been sent
    check_already_sent_early = len(AssignmentNotificationSent.objects.filter(assignment_id=assignment_id, notification_type='early')) > 0

    # assignment with earlier 'early' notification found, of which the deadline has not passed yet, which has not yet been sent, which is not already planned
    if (planned_time is None or (due_date - time_to_deadline < planned_time)) and due_date > datetime.timestamp(datetime.today()) and not check_already_sent_early and not (planned_assignment_id == assignment_id and planned_type == 'early'):
        planned_assignment_id = assignment_id
        planned_type = 'early'
        planned_time = due_date - time_to_deadline
    else:
        # check if a late notification has already been sent
        check_already_sent_late = len(AssignmentNotificationSent.objects.filter(assignment_id=assignment_id, notification_type='late')) > 0

        # assignment with earlier 'late' notification found, which has not yet been sent and which is not already planned
        if (planned_time is None or due_date < planned_time) and not check_already_sent_late and not (planned_assignment_id == assignment_id and planned_type == 'late'):
            planned_assignment_id = assignment_id
            planned_type = 'late'
            planned_time = due_date

    return (planned_assignment_id, planned_type, planned_time)


def update_first_assignment_notification_time_all_courses(scheduler):
    """
    Update the stored first assignment of all courses, so they can be scheduled appropriately.

    :param scheduler: SchedulerConfig object to reschedule jobs
    :type scheduler: SchedulerConfig
    """

    course_list = Course.objects.filter(deadline=True)
    for course_object in course_list:
        # Update when notifications need to be send again
        update_first_assignment_notification_time_of_course(course_object.courseId, scheduler)

    remove_outdated_db_assignment_sent_entries()


def remove_deadline_job_if_course_ended(course_id, scheduler):
    """
    Removes the deadline notification job if the given course has ended.

    :param course_id: The ID of the course to check.
    :type course_id: int
    :param scheduler: SchedulerConfig object to reschedule jobs
    :type scheduler: SchedulerConfig
    :return: If the job needed to be removed.
    :rtype: bool
    """

    # Check if the course has passed and thus the notification job should be removed
    if check_if_ended(course_id):
        scheduler.remove_deadline_notification(course_id)
        print('Removing deadline notificaiton job since course ' + str(course_id) + ' has passed. ')
        return True
    return False


def remove_outdated_db_assignment_sent_entries():
    """
    Removes AssignmentNotificationSent entries that are not relevant anymore because the deadline of the related assignment has passed a while ago.
    Therefore notifications will never be send regardless of if it has been sent or still needed to be sent.
    """

    all_assignment_sent_entries = AssignmentNotificationSent.objects.all()
    redundant_deadline = get_datetime_of_outdated_assignments()
    for entry in all_assignment_sent_entries:
        if entry.time < redundant_deadline:
            entry.delete()


def get_datetime_of_outdated_assignments():
    """
    Returns the current date minus one day. From that point assignment notifications should not be send if the deadline was earlier.

    :return: date minus one day.
    :rtype: datetime.datetime
    """

    return datetime.today() - timedelta(days=1)


def get_or_create_first_notificaton_object(course_id):
    """
    Gets the FirstAssignmentOfCourse object from the database.
    If it does not exist for the requested course, it will be created.

    :param course_id: ID of the course of the course object to retrieve from the database.
    :type course_id: int
    :return: Tuple containing the requested FirstAssignmentOfCourse and a boolean that is True if the FirstAssignmentOfCourse was created in the method.
    :rtype: (FirstAssignmentOfCourse, bool)
    """

    first_notification_object = get_first_notification_object(course_id, False)
    object_was_created = first_notification_object is None
    if first_notification_object is None:
        first_notification_object = FirstAssignmentOfCourse(course_id=course_id,
                                                            assignment_id=-1,
                                                            notification_type='late',
                                                            time=None)

    return (first_notification_object, object_was_created)


def update_first_notification_object(first_notification_object, assignment_id, notifcation_type, time):
    """
    Gets the FirstAssignmentOfCourse object from the database.
    If it does not exist for the requested course, it will be created.

    :param first_notification_object: FirstAssignmentOfCourse object that needs to be updated.
    :type first_notification_object: FirstAssignmentOfCourse
    :param assignmen_id: ID of the assignment the notification is for.
    :type assignmen_id: int
    :param notifcation_type: Type of planned notification ('early' or 'late').
    :type notifcation_type: str
    :param time: Timestamp of when the notification will need to be send.
    :type time: int
    :return: FirstAssignmentOfCourse object that is updated.
    :rtype: FirstAssignmentOfCourse
    """

    first_notification_object.assignment_id = assignment_id
    first_notification_object.notification_type = notifcation_type
    first_notification_object.time = None if time is None else datetime.fromtimestamp(time)
    first_notification_object.save()

    return first_notification_object


def get_time_before_deadline(course_id):
    """Returns the timestamp of time before deadline when early notification should be send ("the deadline will pass soon") while error handling.

    :param course_id: ID of the course of the course object to retrieve from the database.
    :type course_id: int
    :return: Timestamp of length of notification time before deadline
    :rtype: int
    """

    course = get_course_from_db(course_id)
    if course is not None:
        return course.hours_before * 3600
    else:
        return None


def get_first_notification_object(course_id, error_on_not_found=True):
    """Returns the timestamp of time before deadline when early notification should be send ("the deadline will pass soon") while error handling.

    :param course_id: ID of the course of the course object to retrieve from the database.
    :type course_id: int
    :param error_on_not_found: True if an exception needs to be thrown when requested object is not found
    :type error_on_not_found: bool
    :return: Requested FirstAssignmentOfCourse object
    :rtype: scheduler.models.FirstAssignmentOfCourse
    """

    try:
        return FirstAssignmentOfCourse.objects.get(course_id=course_id)
    except FirstAssignmentOfCourse.DoesNotExist:
        if error_on_not_found:
            print("Course: " + str(course_id) + " could not be found in FirstAssignmentOfCourse when searched in get_first_notification_object")
        return None
    except FirstAssignmentOfCourse.MultipleObjectsReturned:
        print("Course: " + str(course_id) + " has multiple entries in FirstAssignmentOfCourse when searched in get_first_notification_object")
        return None
