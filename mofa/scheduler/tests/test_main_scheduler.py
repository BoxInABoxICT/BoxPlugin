# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
import datetime
import json
from time import sleep
from unittest.mock import patch

from courses.models import Course
from django.test import TestCase
from scheduler import deadline_manager
from scheduler import inactivity_courses as inactivity
from scheduler import main_scheduler
from scheduler.models import (AssignmentNotificationSent, CronJob,
                              FirstAssignmentOfCourse, InactivityNotificationSent)

from . import test_data


def get_test_scheduler():
    sched = main_scheduler.SchedulerConfig()
    sched.scheduler.pause()
    main_scheduler.main_scheduler = sched
    return sched


def make_test_course(course_id=2, hours_before=24):
    if len(Course.objects.filter(courseId=course_id)) > 0:
        return

    c = Course(courseId=course_id,
               hours_before=hours_before,
               name='Test Course',
               platform='Moodle',
               inactivity=False,
               inactivity_time=7,
               deadline=False,
               version_time=datetime.datetime.today())
    c.save()
    return c


class MainSchedulerTest(TestCase):

    @patch('scheduler.main_scheduler.SchedulerConfig.add_cron_job')
    def test_add_inactivity_notification(self, add_cron):
        sched = get_test_scheduler()
        sched.add_inactivity_notification(2, 86400)

        add_cron.assert_called_once()
        add_cron.assert_called_with(inactivity.create_job, 2, 'inactive', 'cron', {'second': '0,10,20,30,40,50'}, args=[2, 86400, main_scheduler.main_scheduler], persistent_args=[2, 86400])

    @patch('scheduler.main_scheduler.SchedulerConfig.add_cron_job')
    def test_add_deadline_notification(self, add_cron):
        sched = get_test_scheduler()
        sched.add_deadline_notification(2)

        add_cron.assert_any_call(deadline_manager.update_first_assignment_notification_time_all_courses,
                                 None,
                                 'updatefirstdeadlines',
                                 'cron',
                                 main_scheduler.GLOBAL_DEADLINE_CHECK_TRIGGER_KWARGS,
                                 args=[sched],
                                 persistent_args=[],
                                 job_name='updatefirstdeadlines')
        add_cron.assert_called_with(deadline_manager.check_course_assignment_notifications, 2, 'assignment_check', 'date', {}, args=[2, sched], persistent_args=[2])

        # Check if second time update is not called
        add_cron.reset_mock()
        sched.jobs['updatefirstdeadlines'] = None

        sched.add_deadline_notification(2)

        add_cron.assert_called_with(deadline_manager.check_course_assignment_notifications, 2, 'assignment_check', 'date', {}, args=[2, sched], persistent_args=[2])
        add_cron.assert_called_once()

    def test_register_job_to_model(self):
        main_scheduler.SchedulerConfig.register_job_to_model(0, 'assignment_check', '0assignment_check', [0])

        jobs = CronJob.objects.all()
        self.assertEqual(len(jobs), 1)
        job = jobs[0]

        self.assertEqual(job.name, '0assignment_check')
        self.assertEqual(job.course, 0)
        self.assertEqual(job.job_type, 'assignment_check')
        self.assertEqual(json.loads(job.args_json), [0])

        # Check that the same job cannot be added twice
        main_scheduler.SchedulerConfig.register_job_to_model(0, 'assignment_check', '0assignment_check', [0])

        jobs = CronJob.objects.all()
        self.assertEqual(len(jobs), 1)

    def test_remove_job_from_model(self):
        main_scheduler.SchedulerConfig.register_job_to_model(0, 'assignment_check', '0assignment_check', [0])

        jobs = CronJob.objects.all()
        self.assertEqual(len(jobs), 1)

        main_scheduler.SchedulerConfig.remove_job_from_model('0assignment_check')

        jobs = CronJob.objects.all()
        self.assertEqual(len(jobs), 0)

    def test_add_cron_job(self):
        sched = get_test_scheduler()

        now = datetime.datetime.today()
        an_hour = datetime.timedelta(hours=1)
        over_an_hour = now + an_hour

        # Add job to database and scheduler
        sched.add_cron_job(deadline_manager.check_course_assignment_notifications, 2, 'assignment_check', 'date', {'run_date': over_an_hour}, args=[2, sched], persistent_args=[2])

        self.assertEqual(len(sched.jobs), 1)
        job = sched.jobs['2assignment_check']
        self.assertEqual(job.func, deadline_manager.check_course_assignment_notifications)
        self.assertEqual(job.args, (2, sched))
        self.assertEqual(job.next_run_time.replace(tzinfo=None), over_an_hour)

        self.assertIs(sched.scheduler.get_job(job.id), job)

        jobs = CronJob.objects.all()
        self.assertEqual(len(jobs), 1)

    def test_add_and_remove_job_from_model(self):
        sched = get_test_scheduler()

        # Check if there are no errors when trying to remove a none existing job
        sched.remove_job('0assignment_check')

        self.assertEqual(len(sched.jobs), 0)
        jobs = CronJob.objects.all()
        self.assertEqual(len(jobs), 0)

        # Add job (and update job) to database and scheduler
        sched.add_deadline_notification(0)

        self.assertEqual(len(sched.jobs), 2)
        jobs = CronJob.objects.all()
        self.assertEqual(len(jobs), 2)

        # Add another job to database and scheduler
        sched.add_deadline_notification(1)

        self.assertEqual(len(sched.jobs), 3)
        jobs = CronJob.objects.all()
        self.assertEqual(len(jobs), 3)

        # Remove first job
        sched.remove_job('0assignment_check')

        self.assertEqual(len(sched.jobs), 2)
        jobs = CronJob.objects.all()
        self.assertEqual(len(jobs), 2)

        # Remove second job
        sched.remove_job('1assignment_check')

        self.assertEqual(len(sched.jobs), 1)
        jobs = CronJob.objects.all()
        self.assertEqual(len(jobs), 1)

        # Remove update job
        sched.remove_job('updatefirstdeadlines')

        self.assertEqual(len(sched.jobs), 0)
        jobs = CronJob.objects.all()
        self.assertEqual(len(jobs), 0)

    @patch('time.time', return_value=1573775000)
    def test_reschedule_job(self, time):
        sched = get_test_scheduler()

        now = datetime.datetime.today()
        an_hour = datetime.timedelta(hours=1)
        an_hour_earlier = now - an_hour
        over_an_hour = now + an_hour

        # Check if doesn't crash with an invalid job
        sched.reschedule_job('testing_reschedule', 'date', {'run_date': over_an_hour}, over_an_hour)

        sched.add_cron_job((lambda text: print(text)), None, 'assignment_check', 'date', {}, args=['testing_reschedule'], persistent_args=['testing_reschedule'], job_name='testing_reschedule')

        self.assertEqual(len(sched.jobs), 1)
        sched.reschedule_job('testing_reschedule', 'date', {'run_date': over_an_hour}, over_an_hour)
        self.assertEqual(sched.jobs['testing_reschedule'].next_run_time.replace(tzinfo=None), over_an_hour)

        sched.reschedule_job('testing_reschedule', 'date', {'run_date': an_hour_earlier}, an_hour_earlier)
        self.assertEqual(sched.jobs['testing_reschedule'].next_run_time.replace(tzinfo=None), now)

    def test_remove_deadline_notification(self):
        sched = get_test_scheduler()
        make_test_course(2)

        sched.add_deadline_notification(2)

        related_first = FirstAssignmentOfCourse(assignment_id=2, notification_type='late', time=datetime.datetime.today(), course_id=2)
        related_first.save()
        other_first = FirstAssignmentOfCourse(assignment_id=2, notification_type='late', time=datetime.datetime.today(), course_id=3)
        other_first.save()

        sched.remove_deadline_notification(2)

        # Assert job cleanup
        self.assertNotIn('2assignment_check', sched.jobs)
        self.assertEqual(list(CronJob.objects.filter(course=2)), [])

        # Assert FirstAssignmentOfCourse cleanup
        self.assertEqual(len(FirstAssignmentOfCourse.objects.all()), 1)
        self.assertEqual(list(FirstAssignmentOfCourse.objects.filter(course_id=2)), [])
        self.assertNotEqual(list(FirstAssignmentOfCourse.objects.filter(course_id=3)), [])

    def test_remove_inactivity_notification(self):
        sched = get_test_scheduler()
        make_test_course(2)

        sched.add_inactivity_notification(2, 1)

        related_entry = InactivityNotificationSent('2', json.dumps({'1': '1', '2': '1'}))
        related_entry.save()
        other_entry = InactivityNotificationSent('3', json.dumps({'1': '1', '2': '1'}))
        other_entry.save()

        sched.remove_inactivity_notification(2)

        # Assert job cleanup
        self.assertNotIn('2inactive', sched.jobs)
        self.assertEqual(list(CronJob.objects.filter(course=2)), [])

        # Assert FirstAssignmentOfCourse cleanup
        self.assertEqual(len(InactivityNotificationSent.objects.all()), 1)
        self.assertEqual(list(InactivityNotificationSent.objects.filter(course_id=2)), [])
        self.assertNotEqual(list(InactivityNotificationSent.objects.filter(course_id=3)), [])

    @patch('scheduler.deadline_manager.check_course_assignment_notifications')
    @patch('scheduler.deadline_manager.update_first_assignment_notification_time_of_course')
    def test_cron_persistent_recreate(self, update_notification, check_notification):
        # Create empty scheduler
        sched1 = get_test_scheduler()

        # Create 2 jobs
        sched1.add_cron_job(
            lambda x: print(x),
            1,
            'assignment_check',
            'date',
            {},
            args=[1],
            persistent_args=[1]
        )
        sched1.add_cron_job(
            lambda x: print(x),
            2,
            'updatefirstdeadlines',
            'date',
            {},
            args=[1],
            persistent_args=[1],
            job_name='updatefirstdeadlines'
        )

        # Create new scheduler
        sched2 = get_test_scheduler()

        # Check if new scheduler has jobs of the old scheduler
        self.assertEqual(len(sched1.jobs), 2)
        self.assertEqual(len(sched1.jobs), len(sched2.jobs))
        for job_name, job in sched1.jobs.items():
            self.assertIn(job_name, sched2.jobs)

    def test_clear_all_persistent_jobs(self):
        sched = get_test_scheduler()

        # Check if clear on empty database results in no errors
        main_scheduler.SchedulerConfig.clear_all_persistent_jobs()
        self.assertEqual(len(CronJob.objects.all()), 0)

        # Create multiple jobs
        sched.add_cron_job(
            lambda x: print(x),
            1,
            'assignment_check',
            'date',
            {},
            args=[1],
            persistent_args=[1]
        )
        sched.add_cron_job(
            lambda x: print(x),
            2,
            'updatefirstdeadlines',
            'date',
            {},
            args=[1],
            persistent_args=[1]
        )

        # Call clear
        main_scheduler.SchedulerConfig.clear_all_persistent_jobs()

        # Check if all jobs are removed
        self.assertEqual(len(CronJob.objects.all()), 0)

    def test_prune_persistent_jobs(self):
        sched = get_test_scheduler()

        # Create multiple jobs
        sched.add_cron_job(
            lambda x: print(x),
            1,
            'assignment_check',
            'date',
            {},
            args=[1],
            persistent_args=[1]
        )
        sched.add_cron_job(
            lambda x: print(x),
            1,
            'updatefirstdeadlines',
            'cron',
            {'second': '0,10,20,30,40,50'},
            args=[sched],
            persistent_args=[1],
            job_name='updatefirstdeadlines'
        )
        sched.add_cron_job(
            lambda x: print(x),
            2,
            'assignment_check',
            'date',
            {},
            args=[1],
            persistent_args=[1]
        )

        # Make one job invalid
        invalid_job = CronJob.objects.get(name='1assignment_check')
        invalid_job.args_json = 'undefined'
        invalid_job.save()

        # Call prune
        sched.prune_persistent_jobs()

        # Check if only invalid job was removed
        self.assertEqual(len(CronJob.objects.all()), 2)
        self.assertEqual(CronJob.objects.get(name='2assignment_check').name, '2assignment_check')

        # Check prune on create SchedulerConfig
        # Create invalid
        sched.add_cron_job(
            lambda x: print(x),
            1,
            'assignment_check',
            'date',
            {},
            args=[1],
            persistent_args=[1]
        )
        invalid_job = CronJob.objects.get(name='1assignment_check')
        invalid_job.args_json = 'undefined'
        invalid_job.save()

        sched = get_test_scheduler()

        # Check if only invalid job was removed
        self.assertEqual(len(CronJob.objects.all()), 2)
        self.assertEqual(CronJob.objects.get(name='2assignment_check').name, '2assignment_check')


class MainSchedulerIntegrationTest(TestCase):

    @patch('assistants.moodle.get_course_by_id_field', return_value=test_data.test_get_courses_by_id_ended)
    @patch('assistants.moodle.get_enrolled_users', return_value=test_data.test_get_enrolled_users)
    @patch('assistants.moodle.get_assignment_status', return_value=test_data.test_assignment_completion_check)
    @patch('assistants.moodle.get_assignments', return_value=test_data.test_get_assignments_data)
    @patch('scheduler.deadline_manager.send_warnings')
    @patch('time.time', return_value=1573777061)
    def test_sending_deadline_notification(self, time, send_warnings, get_assignments, get_assignment_status, enrolled_users, check_if_ended):
        sched = get_test_scheduler()
        course = make_test_course()

        sched.add_deadline_notification(2)

        sched.jobs['2assignment_check'].func(*sched.jobs['2assignment_check'].args)

        send_warnings.assert_called_with([('4', 'The deadline for Learning booleans has passed.')])

        assignments_sent = AssignmentNotificationSent.objects.all()
        self.assertEqual(len(assignments_sent), 2)
        self.assertEqual(assignments_sent[0].name, '6late')
        self.assertEqual(assignments_sent[1].name, '9late')
