# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
from datetime import datetime, timedelta
from unittest.mock import call, patch

from courses.models import Course
from django.test import TestCase
from scheduler import deadline_manager, main_scheduler
from scheduler.models import (AssignmentNotificationSent,
                              FirstAssignmentOfCourse,
                              CronJob)
from scheduler.tests.test_main_scheduler import get_test_scheduler, make_test_course

from . import test_data


class DeadlineManagerTest(TestCase):

    @patch('assistants.moodle.get_assignments', return_value=test_data.test_get_assignments_data)
    def test_get_assignments(self, a):
        json_result = deadline_manager.get_assignments(2)

        self.assertEqual(json_result, test_data.test_get_assignments_check)

    @patch('assistants.moodle.get_assignments', return_value=test_data.test_get_assignments_data)
    def test_get_deadlines_between(self, a):
        json_result = deadline_manager.get_assignments(2)

        passed_deadlines = deadline_manager.get_deadlines_between(json_result, 1573776059, 1573776061)
        test_dict = {6: ('Learning basic loops', 1573776060), 9: ('Learning booleans', 1573776060)}
        self.assertEqual(passed_deadlines, test_dict)

        empty_deadlines = deadline_manager.get_deadlines_between(json_result, 0, 1)
        self.assertEqual(empty_deadlines, {})

    @patch('assistants.moodle.get_assignment_status', return_value=test_data.test_assignment_completion_check)
    def test_check_assignment_completion(self, a):
        self.assertEqual(deadline_manager.check_assignment_completion(4, 6, 2), True)
        self.assertEqual(deadline_manager.check_assignment_completion(4, 9, 2), False)

    @patch('assistants.moodle.get_enrolled_users', return_value=test_data.test_get_enrolled_users)
    def test_get_users(self, a):
        self.assertEqual(deadline_manager.get_users(2), ['4'])

    @patch('time.time')
    def test_convert_time(self, a):
        a.return_value = 5000
        due_time1 = deadline_manager.convert_time(5060)
        a.return_value = 6000
        due_time2 = deadline_manager.convert_time(10000)
        self.assertEqual(due_time1, (0, 1))
        self.assertEqual(due_time2, (1, 6))

    def test_prep_late_warning(self):
        message = deadline_manager.prep_late_warning('test_assignment')
        self.assertEqual(message, 'The deadline for test_assignment has passed.')

    def test_prep_early_warning(self):
        message = deadline_manager.prep_early_warning(1, 30, "test_assignment")
        self.assertEqual(message, 'The deadline for test_assignment is in 1 hours and 30 minutes.')

    @patch('assistants.moodle.send_bulk_different_messages')
    @patch('time.time', return_value=0)
    def test_send_warnings(self, a, b):
        deadline_manager.send_warnings([(2, "test message"), (3, "testing message")])
        b.assert_called_with([(2, 'test message'), (3, 'testing message')])

    @patch('time.time', return_value=1573777061)
    def test_register_assignment_notification(self, time):

        deadline_manager.register_assignment_notification(1, 'late', datetime.today())

        assignments_sent = AssignmentNotificationSent.objects.all()
        self.assertEqual(len(assignments_sent), 1)

        assignment = assignments_sent[0]
        self.assertEqual(assignment.notification_type, 'late')
        self.assertEqual(assignment.assignment_id, 1)
        self.assertEqual(assignment.time, datetime.today())

    @patch('builtins.print')
    def test_get_time_before_deadline(self, print_mock):
        # Test without a course in the database
        result = deadline_manager.get_time_before_deadline(2)
        print_mock.assert_called_with("Course: 2 could not be found in Course when searched in get_course_from_db")
        print_mock.assert_called_once()

        self.assertIs(result, None)

        # Test with course
        make_test_course()

        result = deadline_manager.get_time_before_deadline(2)

        self.assertEqual(result, 24 * 3600)

    @patch('builtins.print')
    def test_get_first_notification_object(self, print_mock):
        # Test without a first notification in the database
        result1 = deadline_manager.get_first_notification_object(2, False)
        result2 = deadline_manager.get_first_notification_object(2, True)
        print_mock.assert_called_with("Course: 2 could not be found in FirstAssignmentOfCourse when searched in get_first_notification_object")
        print_mock.assert_called_once()

        self.assertIs(result1, None)
        self.assertIs(result2, None)

        # Test with first notification in the database
        dt = datetime.today()
        FirstAssignmentOfCourse(course_id=2, assignment_id=24, notification_type='late', time=dt).save()
        result3 = deadline_manager.get_first_notification_object(2)

        self.assertEqual(len(FirstAssignmentOfCourse.objects.filter(course_id=2)), 1)
        self.assertEqual(result3, FirstAssignmentOfCourse.objects.get(course_id=2))

    @patch('time.time', return_value=1573777061)
    def test_remove_outdated_db_assignment_sent_entries(self, time):
        valid_entry = AssignmentNotificationSent('1late', 1, 'late', datetime.today())
        valid_entry.save()

        exactly_on_border_entry = AssignmentNotificationSent('2late', 2, 'late', datetime.today() - timedelta(days=1))
        exactly_on_border_entry.save()

        outdated_entry_1 = AssignmentNotificationSent('3late', 3, 'late', datetime.today() - timedelta(days=1, minutes=1))
        outdated_entry_1.save()

        outdated_entry_2 = AssignmentNotificationSent('4late', 4, 'late', datetime.today() - timedelta(days=2))
        outdated_entry_2.save()

        deadline_manager.remove_outdated_db_assignment_sent_entries()

        # Assert that only the valid and exactly_on_border entries have not been removed
        self.assertEqual(len(AssignmentNotificationSent.objects.all()), 2)
        self.assertNotEqual(AssignmentNotificationSent.objects.filter(name='1late'), [])
        self.assertNotEqual(AssignmentNotificationSent.objects.filter(name='2late'), [])


class CheckCourseAssignmentNotificationsTest(TestCase):

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_ended)
    @patch('scheduler.deadline_manager.update_first_assignment_notification_time_of_course')
    @patch('assistants.moodle.get_enrolled_users', return_value=test_data.test_get_enrolled_users)
    @patch('assistants.moodle.get_assignment_status', return_value=test_data.test_assignment_completion_check)
    @patch('assistants.moodle.get_assignments', return_value=test_data.test_get_assignments_data)
    @patch('scheduler.deadline_manager.send_warnings')
    @patch('time.time', return_value=1573777061)
    def test_check_course_assignment_notifications_late(self, time, send_warnings, get_assignments, status,
                                                        enrolled_users, update, check_if_ended):
        """Test late notifcation check"""
        # Init scheduler
        sched = get_test_scheduler()

        # Init course
        make_test_course()

        deadline_manager.check_course_assignment_notifications(2, sched)

        send_warnings.assert_called_with([('4', 'The deadline for Learning booleans has passed.')])

        assignments_sent = AssignmentNotificationSent.objects.all()
        self.assertEqual(len(assignments_sent), 2)
        self.assertEqual(assignments_sent[0].name, '6late')
        self.assertEqual(assignments_sent[1].name, '9late')

        assignments_to_check_on_update = []
        update.assert_called_with(2, sched, assignments_to_check_on_update)

        # Trigger twice but only send notification once
        deadline_manager.check_course_assignment_notifications(2, sched)

        send_warnings.assert_called_once()

        assignments_sent = AssignmentNotificationSent.objects.all()
        self.assertEqual(len(assignments_sent), 2)
        self.assertEqual(assignments_sent[0].name, '6late')
        self.assertEqual(assignments_sent[1].name, '9late')

        update.assert_called_with(2, sched, assignments_to_check_on_update)
        self.assertEqual(len(update.mock_calls), 2)

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_ended)
    @patch('scheduler.deadline_manager.update_first_assignment_notification_time_of_course')
    @patch('assistants.moodle.get_enrolled_users', return_value=test_data.test_get_enrolled_users)
    @patch('assistants.moodle.get_assignment_status', return_value=test_data.test_assignment_completion_check)
    @patch('assistants.moodle.get_assignments', return_value=test_data.test_get_assignments_data)
    @patch('scheduler.deadline_manager.send_warnings')
    @patch('time.time', return_value=1573775000)
    def test_check_course_assignment_notifications_early(self, time, send_warnings, get_assignments,
                                                         status, enrolled_users, update, check_if_ended):
        """Test early notification check"""
        # Init scheduler
        sched = get_test_scheduler()

        # Init course
        make_test_course()

        deadline_manager.check_course_assignment_notifications(2, sched)

        send_warnings.assert_called_with([('4', 'The deadline for Learning booleans is in 0 hours and 17 minutes.')])

        assignments_sent = AssignmentNotificationSent.objects.all()
        self.assertEqual(len(assignments_sent), 2)
        self.assertEqual(assignments_sent[0].name, '6early')
        self.assertEqual(assignments_sent[1].name, '9early')

        assignments_to_check_on_update = deadline_manager.get_assignments(2)
        update.assert_called_with(2, sched, assignments_to_check_on_update)

        # Trigger twice but only send notification once
        deadline_manager.check_course_assignment_notifications(2, sched)

        send_warnings.assert_called_once()

        assignments_sent = AssignmentNotificationSent.objects.all()
        self.assertEqual(len(assignments_sent), 2)
        self.assertEqual(assignments_sent[0].name, '6early')
        self.assertEqual(assignments_sent[1].name, '9early')

        update.assert_called_with(2, sched, assignments_to_check_on_update)
        self.assertEqual(len(update.mock_calls), 2)

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_ended)
    @patch('scheduler.deadline_manager.update_first_assignment_notification_time_of_course')
    @patch('assistants.moodle.get_enrolled_users', return_value=test_data.test_get_enrolled_users)
    @patch('assistants.moodle.get_assignment_status', return_value=test_data.test_assignment_completion_check)
    @patch('assistants.moodle.get_assignments', return_value=test_data.test_get_assignments_data)
    @patch('scheduler.deadline_manager.send_warnings')
    @patch('time.time', return_value=1573863461)
    def test_check_course_assignment_notifications_old_assignment(self, time, send_warnings, get_assignments,
                                                                  status, enrolled_users, update, check_if_ended):
        """Test with more than a day old notification, which should be skipped"""
        # Init scheduler
        sched = get_test_scheduler()

        # Init course
        make_test_course()

        deadline_manager.check_course_assignment_notifications(2, sched)

        send_warnings.assert_not_called()

        assignments_to_check_on_update = []
        update.assert_called_with(2, sched, assignments_to_check_on_update)

        # Test when already sent
        assignments_sent = AssignmentNotificationSent('6early', 6, 'early', datetime.today())
        assignments_sent.save()
        assignments_sent = AssignmentNotificationSent('9early', 9, 'early', datetime.today())
        assignments_sent.save()
        deadline_manager.check_course_assignment_notifications(2, sched)

        send_warnings.assert_not_called()

        assignments_to_check_on_update = []
        update.assert_called_with(2, sched, assignments_to_check_on_update)

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_ended)
    @patch('scheduler.deadline_manager.update_first_assignment_notification_time_of_course')
    @patch('assistants.moodle.get_enrolled_users', return_value=test_data.test_get_enrolled_users)
    @patch('assistants.moodle.get_assignment_status', return_value=test_data.test_assignment_completion_check)
    @patch('assistants.moodle.get_assignments', return_value=test_data.test_get_assignments_data)
    @patch('scheduler.deadline_manager.send_warnings')
    @patch('time.time', return_value=1573777061)
    def test_check_course_assignment_notifications_none(self, time, send_warnings, get_assignments,
                                                        status, enrolled_users, update, check_if_ended):
        """Test no notification check"""
        # Init scheduler
        sched = get_test_scheduler()

        # Test without course
        deadline_manager.check_course_assignment_notifications(2, sched)
        send_warnings.assert_not_called()
        assignments_to_check_on_update = []
        update.assert_called_with(2, sched, assignments_to_check_on_update)

        # Test when already sent
        assignments_sent = AssignmentNotificationSent('9early', 9, 'early', datetime.today())
        assignments_sent.save()
        assignments_sent = AssignmentNotificationSent('9late', 9, 'late', datetime.today())
        assignments_sent.save()
        assignments_sent = AssignmentNotificationSent('6early', 6, 'early', datetime.today())
        assignments_sent.save()
        assignments_sent = AssignmentNotificationSent('6late', 6, 'late', datetime.today())
        assignments_sent.save()

        deadline_manager.check_course_assignment_notifications(2, sched)
        send_warnings.assert_not_called()
        assignments_to_check_on_update = []
        update.assert_called_with(2, sched, assignments_to_check_on_update)

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_ended)
    @patch('scheduler.deadline_manager.update_first_assignment_notification_time_of_course')
    @patch('assistants.moodle.get_enrolled_users', return_value=test_data.test_get_enrolled_users)
    @patch('assistants.moodle.get_assignment_status', return_value=test_data.test_assignment_completion_check)
    @patch('assistants.moodle.get_assignments', return_value=test_data.test_get_assignments_data)
    @patch('scheduler.deadline_manager.send_warnings')
    @patch('time.time', return_value=1573604261)
    def test_check_course_assignment_notifications_not_yet(self, time, send_warnings, get_assignments,
                                                           status, enrolled_users, update, check_if_ended):
        """Test notification which should send in the future"""
        # Init scheduler
        sched = get_test_scheduler()

        # Init course
        make_test_course()

        deadline_manager.check_course_assignment_notifications(2, sched)
        send_warnings.assert_not_called()
        assignments_to_check_on_update = deadline_manager.get_assignments(2)
        update.assert_called_with(2, sched, assignments_to_check_on_update)

        # Test when already sent as early
        assignments_sent = AssignmentNotificationSent('6early', 6, 'early', datetime.today())
        assignments_sent.save()
        assignments_sent = AssignmentNotificationSent('9early', 9, 'early', datetime.today())
        assignments_sent.save()

        deadline_manager.check_course_assignment_notifications(2, sched)
        send_warnings.assert_not_called()
        update.assert_called_with(2, sched, assignments_to_check_on_update)

        # Test when already sent as late
        assignments_sent = AssignmentNotificationSent('6late', 6, 'late', datetime.today())
        assignments_sent.save()
        assignments_sent = AssignmentNotificationSent('9late', 9, 'late', datetime.today())
        assignments_sent.save()

        deadline_manager.check_course_assignment_notifications(2, sched)
        send_warnings.assert_not_called()
        assignments_to_check_on_update = []
        update.assert_called_with(2, sched, assignments_to_check_on_update)

        @patch('scheduler.deadline_manager.update_first_assignment_notification_time_of_course')
        @patch('scheduler.deadline_manager.send_single_assignment_notification')
        @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_ended)
        @patch('assistants.moodle.get_assignments', return_value=test_data.test_get_assignments_data)
        @patch('time.time', return_value=1800000000)
        def test_check_course_assignment_notifications_course_ended(self, time, get_assignments, check_if_ended, send_single, update_first):
            sched = get_test_scheduler()
            make_test_course()

            # Add deadline notification job
            sched.add_deadline_notification(2)
            # Force job because scheduler is paused while testing
            deadline_manager.check_course_assignment_notifications(2, sched)

            # Assert that nothing was called because the course has already ended
            send_single.assert_not_called()
            update_first.assert_not_called()

            # Assert that the job has been removed
            self.assertNotIn('2assignment_check', sched.jobs)
            self.assertEqual(list(CronJob.objects.filter(course=2)), [])
            self.assertEqual(len(FirstAssignmentOfCourse.objects.all()), 0)


class UpdateFirstAssignmentNotificationTimeOfCourseTest(TestCase):

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_ended)
    @patch('assistants.moodle.get_assignments', return_value=test_data.test_get_assignments_data)
    @patch('scheduler.main_scheduler.SchedulerConfig.reschedule_job')
    @patch('time.time', return_value=1573604261)
    def test_update_first_assignment_notification_time_of_course_late(self, time, reschedule, get_assignments, check_if_ended):
        sched = get_test_scheduler()
        dt_of_deadline = datetime.fromtimestamp(1573776060)
        dt_of_early = datetime.fromtimestamp(1573776060 - 86400)

        # Test without course
        deadline_manager.update_first_assignment_notification_time_of_course(2, sched)
        # Assert
        reschedule.assert_not_called()
        self.assertEqual(len(FirstAssignmentOfCourse.objects.all()), 0)

        # Test with course
        make_test_course()
        # Run
        deadline_manager.update_first_assignment_notification_time_of_course(2, sched)
        # Assert
        reschedule.assert_called_with('2assignment_check', 'date', {'run_date': dt_of_early}, dt_of_early)
        reschedule.assert_called_once()
        self.assertEqual(len(FirstAssignmentOfCourse.objects.all()), 1)
        self.assertEqual(FirstAssignmentOfCourse.objects.get(course_id=2).time, dt_of_early)

        # Test with filled in assignments_to_check
        # Clear previous result
        FirstAssignmentOfCourse.objects.get(course_id=2).delete()
        # Run
        deadline_manager.update_first_assignment_notification_time_of_course(2, sched, deadline_manager.get_assignments(2))
        # Assert
        reschedule.assert_called_with('2assignment_check', 'date', {'run_date': dt_of_early}, dt_of_early)
        self.assertEqual(len(FirstAssignmentOfCourse.objects.all()), 1)
        self.assertEqual(FirstAssignmentOfCourse.objects.get(course_id=2).time, dt_of_early)

        # Test with early notification already sent
        assignments_sent = AssignmentNotificationSent('6early', 6, 'early', datetime.today())
        assignments_sent.save()
        assignments_sent = AssignmentNotificationSent('9early', 9, 'early', datetime.today())
        assignments_sent.save()
        # Clear previous result
        FirstAssignmentOfCourse.objects.get(course_id=2).delete()
        # Run
        deadline_manager.update_first_assignment_notification_time_of_course(2, sched)
        # Assert
        reschedule.assert_called_with('2assignment_check', 'date', {'run_date': dt_of_deadline}, dt_of_deadline)
        self.assertEqual(len(FirstAssignmentOfCourse.objects.all()), 1)
        self.assertEqual(FirstAssignmentOfCourse.objects.get(course_id=2).time, dt_of_deadline)

        # Test with filled in assignments_to_check
        # Clear previous result
        FirstAssignmentOfCourse.objects.get(course_id=2).delete()
        # Run
        deadline_manager.update_first_assignment_notification_time_of_course(2, sched, deadline_manager.get_assignments(2))
        # Assert
        reschedule.assert_called_with('2assignment_check', 'date', {'run_date': dt_of_deadline}, dt_of_deadline)
        self.assertEqual(len(FirstAssignmentOfCourse.objects.all()), 1)
        self.assertEqual(FirstAssignmentOfCourse.objects.get(course_id=2).time, dt_of_deadline)

        # Test with FirstAssignmentOfCourse.time not being empty
        AssignmentNotificationSent.objects.get(name='6early').delete()
        AssignmentNotificationSent.objects.get(name='9early').delete()
        # Run
        deadline_manager.update_first_assignment_notification_time_of_course(2, sched)
        # Assert
        reschedule.assert_called_with('2assignment_check', 'date', {'run_date': dt_of_early}, dt_of_early)
        self.assertEqual(len(FirstAssignmentOfCourse.objects.all()), 1)
        self.assertEqual(FirstAssignmentOfCourse.objects.get(course_id=2).time, dt_of_early)

        # Test with no unsent assignments left
        assignments_sent = AssignmentNotificationSent('6early', 6, 'early', datetime.today())
        assignments_sent.save()
        assignments_sent = AssignmentNotificationSent('6late', 6, 'late', datetime.today())
        assignments_sent.save()
        assignments_sent = AssignmentNotificationSent('9early', 9, 'early', datetime.today())
        assignments_sent.save()
        assignments_sent = AssignmentNotificationSent('9late', 9, 'late', datetime.today())
        assignments_sent.save()
        reschedule.reset_mock()
        FirstAssignmentOfCourse.objects.get(course_id=2).delete()
        # Run
        deadline_manager.update_first_assignment_notification_time_of_course(2, sched)
        # Assert
        reschedule.assert_not_called()
        self.assertEqual(len(FirstAssignmentOfCourse.objects.all()), 1)

    @patch('scheduler.deadline_manager.update_first_notification_check_single_assignment')
    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_ended)
    @patch('assistants.moodle.get_assignments', return_value=test_data.test_get_assignments_data)
    @patch('scheduler.main_scheduler.SchedulerConfig.reschedule_job')
    @patch('time.time', return_value=1800000000)
    def test_update_first_assignment_notification_course_ended(self, time, reschedule, get_assignments, check_if_ended, update_single_assignment):
        sched = get_test_scheduler()
        make_test_course()

        # Add deadline notification job
        sched.add_deadline_notification(2)
        # Force job because scheduler is paused while testing
        deadline_manager.update_first_assignment_notification_time_of_course(2, sched)

        # Assert that nothing was called because the course has already ended
        reschedule.assert_not_called()
        update_single_assignment.assert_not_called()
        self.assertEqual(len(FirstAssignmentOfCourse.objects.all()), 0)

        # Assert that the job has been removed
        self.assertNotIn('2assignment_check', sched.jobs)
        self.assertEqual(list(CronJob.objects.filter(course=2)), [])

    @patch('scheduler.utils.check_if_ended', return_value=False)
    @patch('scheduler.deadline_manager.remove_outdated_db_assignment_sent_entries')
    @patch('scheduler.main_scheduler.on_save_course')
    @patch('scheduler.deadline_manager.update_first_assignment_notification_time_of_course')
    def test_update_first_assignment_notification_time_all_courses_with_mock(self, update_first_of_course, on_save_course, remove_outdated_db_assignment_entries, check_if_ended):
        # Init scheduler
        sched = get_test_scheduler()

        # Init test data and corrisponding expected calls
        test_course_ids = [1, 2, 5, 10]
        expected_calls = []
        for c_id in test_course_ids:
            FirstAssignmentOfCourse(course_id=c_id, assignment_id=c_id + 10, notification_type='late', time=None).save()
            course = make_test_course(c_id, 24 * c_id)
            course.deadline = True
            course.save()

            expected_calls.append(call(c_id, sched))

        # Run method
        deadline_manager.update_first_assignment_notification_time_all_courses(sched)

        # Assert results
        update_first_of_course.assert_has_calls(expected_calls)
        remove_outdated_db_assignment_entries.assert_called_once()

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_ended)
    @patch('scheduler.main_scheduler.on_save_course')
    @patch('assistants.moodle.get_assignments', return_value=test_data.test_get_assignments_data)
    @patch('scheduler.main_scheduler.SchedulerConfig.reschedule_job')
    @patch('time.time', return_value=1573604261)
    def test_update_first_assignment_notification_time_all_courses_without_mock(self, time, reschedule, get_assignments, on_save_course, check_if_ended):
        # Init
        sched = get_test_scheduler()
        dt_of_deadline = datetime.fromtimestamp(1573776060)
        dt_of_early = datetime.fromtimestamp(1573776060 - 86400)
        course = make_test_course()
        course.deadline = True
        course.save()

        FirstAssignmentOfCourse(course_id=2, assignment_id=6, notification_type='late', time=None).save()

        # Run method
        deadline_manager.update_first_assignment_notification_time_all_courses(sched)

        # Assert
        reschedule.assert_called_with('2assignment_check', 'date', {'run_date': dt_of_early}, dt_of_early)
        reschedule.assert_called_once()
        self.assertEqual(len(FirstAssignmentOfCourse.objects.all()), 1)
        self.assertEqual(FirstAssignmentOfCourse.objects.get(course_id=2).time, dt_of_early)
