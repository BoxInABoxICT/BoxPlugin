# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Main scheduler file."""
import json
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from courses import models as course_models
from django.conf import settings
from django.db import connection

import scheduler.deadline_manager as deadline_manager
import scheduler.inactivity_courses as inactivity
from scheduler.models import CronJob, FirstAssignmentOfCourse, InactivityNotificationSent
from scheduler.utils import get_course_from_db

GLOBAL_DEADLINE_CHECK_TRIGGER_KWARGS = {'second': '0,10,20,30,40,50'}   # Change for deployment to {'hour': '6, 15'}, change for debugging to {'second': '0,10,20,30,40,50'}


class SchedulerConfig:
    """Start the scheduler and re-add persitent jobs from the database to the scheduler."""

    name = 'scheduler'

    def __init__(self):
        """Instantiate the scheduler and add jobs."""
        self.jobs = {}
        self.scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        self.scheduler.start()

        self.cron_persistent_recreate()

    def cron_persistent_recreate(self):
        """
        Recreates the scheduler from database model when server went down. Retrieves cronjobs from the database and reinitiates them.
        """

        # As this function is called on class init, we need to check if the migrations have been applied.
        # This will fail during the [manage.py makemigrations, migrate] commands as these commands are creating the table.
        if 'scheduler_cronjob' in connection.introspection.table_names():
            persistent_jobs = CronJob.objects.all()
        else:
            persistent_jobs = None

        print('Persistent jobs found: ' + ('None' if persistent_jobs is None else str(len(persistent_jobs))))
        needsPruning_bool = False
        if persistent_jobs is not None:
            i = 0
            for db_job in persistent_jobs:
                i += 1
                # Prints loaded jobs
                # print('i: ' + str(i) + ' Job: ' + str(db_job.name))

                if db_job.args_json == 'undefined':
                    print('args_json are undefined.')
                    needsPruning_bool = True
                    continue

                function = self.get_job_type_function(db_job.job_type)
                if function is None:
                    continue
                args = json.loads(db_job.args_json)
                function(*args)

        if needsPruning_bool:
            self.prune_persistent_jobs()

        print('Loaded ' + str(len(self.jobs)) + ' jobs. ')

    def add_deadline_notification(self, course_id):
        """Adds a deadline notification job to the scheduler of the desired type. Also adds the global check if not enabled already.

        :param course_id: The ID of the course to add assignment deadline notifications to
        :type course_id: int
        """

        # Job for global check for all courses, that checks if assignments have been modified
        global_check_job_type = 'updatefirstdeadlines'
        if global_check_job_type not in self.jobs:
            self.add_cron_job(
                deadline_manager.update_first_assignment_notification_time_all_courses,
                None,
                global_check_job_type,
                'cron',
                GLOBAL_DEADLINE_CHECK_TRIGGER_KWARGS,
                args=[self],
                persistent_args=[],
                job_name=global_check_job_type
            )

        # Job for specific course, that triggers deadline notifications
        self.add_cron_job(
            deadline_manager.check_course_assignment_notifications,
            course_id,
            'assignment_check',
            'date',
            {},
            args=[course_id, self],
            persistent_args=[course_id]
        )

    def add_inactivity_notification(self, course_id, inactivity_time):
        """
        Add scheduler job to send notifications for inactivity of students at 3 AM.

        :param course_id: Course to check the deadlines for.
        :type course_id: int
        :param inactivity_time: Number of days the activity needs to be checked for, default is 7 days.
        :type inactivity_time: int
        """

        inactivity_manager = inactivity.create_job
        self.add_cron_job(
            inactivity_manager,
            course_id,
            'inactive',
            'cron',
            {'second': '0,10,20,30,40,50'},
            args=[course_id, inactivity_time, self],
            persistent_args=[course_id, inactivity_time]
        )

    def add_cron_job(self, function, course_id, job_type, trigger, trigger_kwargs, args=None, persistent_args=None, job_name=None):
        """
        Add a cron job to the scheduler.

        :param function: The function that needs to be performed by the cron job.
        :type: function or str
        :param course_id: Course ID of course relevant for function, used to construct job_name. Supply job_name to overwrite.
        :type course_id: int
        :param job_type: Keyword for job_type defined. Choices are defined in scheduler.models.CronJob.
        :type job_type: str
        :param trigger: BackgroundScheduler trigger type. This determines the scheduling type.
        :type trigger: str
        :param trigger_kwargs: Dictionairy of form {trigger_parameter: 'parameter_value'} used to specify trigger parameters.
        :type trigger_kwargs: {str: str}
        :param args: Arguments that are needed to be send with the function.
        :type args: all types
        :param persistent_args: All arguments needed to call the function to recreate the job.
        :type persistent_args: all types
        :param job_name: Job name to overwrite default constructed job name.
        :type job_name: str
        :return: The job that is created.
        :rtype: job
        """

        if job_name is None:
            job_name = str(course_id) + job_type

        # Do not add jobs that already exist
        if job_name in self.jobs:
            print('Tried to add existing job: ' + job_name)
            return

        kwargs = trigger_kwargs
        kwargs['func'] = function
        kwargs['args'] = args
        kwargs['trigger'] = trigger
        job = self.scheduler.add_job(**kwargs)
        if job is not None and len(CronJob.objects.filter(name=job_name)) == 0:
            SchedulerConfig.register_job_to_model(course_id, job_type, job_name, persistent_args)

        self.jobs[job_name] = job

    def remove_job(self, job_name):
        """
        Remove a scheduled job.

        :param job_name: Name of the job.
        :type job_name: str
        """

        SchedulerConfig.remove_job_from_model(job_name)

        if job_name in self.jobs:
            if self.scheduler.get_job(self.jobs[job_name].id) is not None:
                self.jobs[job_name].remove()
            del self.jobs[job_name]

    def remove_deadline_notification(self, course_id):
        """
        Removes a deadline notification job and all related database data.

        :param course_id: The course id of the course the job is related to.
        :type course_id: int
        """

        # Remove first_notification which belongs to this course's assignment_check
        for first_notification in FirstAssignmentOfCourse.objects.filter(course_id=course_id):
            first_notification.delete()
        # Remove job
        self.remove_job(str(course_id) + 'assignment_check')
        # Remove deadlines notifications from course
        course = get_course_from_db(course_id)
        if course is not None and course.deadline:
            course.deadline = False
            course.save()

    def remove_inactivity_notification(self, course_id):
        """
        Removes a inactivity notification job and all related database data.

        :param course_id: The course id of the course the job is related to.
        :type course_id: int
        """

        # Remove InactivityNotificationSent which is only used for the inactivity job
        for inactivity_sent in InactivityNotificationSent.objects.filter(pk=course_id):
            inactivity_sent.delete()
        # Remove job
        self.remove_job(str(course_id) + 'inactive')
        # Update course object to having no inactivity notification anymore
        course = deadline_manager.get_course_from_db(course_id)
        if course is not None and course.inactivity:
            course.inactivity = False
            course.save()

    def register_job_to_model(course_id, job_type, job_name, args):
        """
        Make a job persistent by adding it to the database.

        :param course_id: The course id of the course the job is related to.
        :type course_id: int
        :param job_type: The type of job for the course. Check scheduler.models.JOB_TYPES for choices.
        :type job_type: str
        :param job_name: Name of the job.
        :type job_name: str
        :param args: All arguments needed to call the function to recreate the job.
        :type args: all types
        """

        db_job = CronJob(name=job_name, course=course_id, job_type=job_type, args_json=json.dumps(args))
        db_job.save()
        print('Registered job: ' + db_job.name)

    def remove_job_from_model(job_name):
        """
        Remove a job from the database making it non-persistent.

        :param job_type: The type of job for the course. Check scheduler.models.JOB_TYPES for choices.
        :type job_type: str
        """

        jobs_found = CronJob.objects.filter(name=job_name)
        for job in jobs_found:
            job.delete()
            print('Removed job from model: ' + job_name)

    def get_job_type_function(self, job_type):
        """
        Get the function needed to recreate a job depending on its type.

        :param job_name: Name of the job.
        :type job_name: str
        :return: Returns the function to recreate the job type
        :rtype: function
        """

        if job_type == 'assignment_check':
            return self.add_deadline_notification
        elif job_type == 'inactive':
            return self.add_inactivity_notification
        else:
            return None

    def clear_all_persistent_jobs():
        """ This function can be handy when debugging, it clears all jobs in the database."""

        persistent_jobs = CronJob.objects.all()

        print('Removing persistent jobs, total: ' + ('None' if persistent_jobs is None else str(len(persistent_jobs))))
        if persistent_jobs is not None:
            i = 0
            for db_job in persistent_jobs:
                i += 1
                name = db_job.name
                CronJob.objects.filter(name=name).delete()
                print('i: ' + str(i) + ' Removed job: ' + str(db_job.name))

    def prune_persistent_jobs(self):
        """ Removes all invalid jobs. That is, jobs with the default 'undefined' value for CronJob.args_json. """

        persistent_jobs = CronJob.objects.all()

        print('Persistent jobs found: ' + ('None' if persistent_jobs is None else str(len(persistent_jobs))))
        if persistent_jobs is not None:
            for db_job in persistent_jobs:
                if db_job.args_json == 'undefined':
                    print('Job: ' + db_job.name + '.args_json are undefined, pruning...')
                    SchedulerConfig.remove_job_from_model(db_job.name)
                    if db_job.name in self.jobs:
                        del self.jobs[db_job.name]

    def reschedule_job(self, job_name, trigger, time_kwargs, date=None):
        """
        Reschedules a job to a different time. If that time has passed, it will be scheduled now.

        :param job_name: Name of the job.
        :type job_name: str
        :param trigger: BackgroundScheduler trigger type. This determines the scheduling type.
        :type trigger: str
        :param trigger_kwargs: Dictionairy of form {trigger_parameter: 'parameter_value'} used to specify trigger parameters.
        :type trigger_kwargs: {str: str}
        :param date: The date it will be rescheduled to. If that date has passed, it will be scheduled now. Step is skippd if date is None.
        :type date: datetime.datetime
        """

        if job_name in self.jobs:
            job = self.jobs[job_name]
            if date is not None and date < datetime.today():
                trigger = 'date'
                # Same as leaving time_kwargs blank {}, but this is used to mock time in the unit tests
                time_kwargs = {'run_date': datetime.today()}
            if self.scheduler.get_job(job.id) is not None:
                self.jobs[job_name] = job.reschedule(trigger=trigger, **time_kwargs)
            else:
                kwargs = time_kwargs
                kwargs['func'] = job.func
                kwargs['args'] = job.args
                kwargs['trigger'] = trigger
                job = self.scheduler.add_job(**kwargs)


# Create static scheduler object responsible for all the scheduling
main_scheduler = SchedulerConfig()


def on_save_course(course_object):
    """
    On save, if deadline or inactivity is checked, add the jobs to the scheduler.

    :param course_object: modified Course object of which jobs need to be modified accordingly.
    :type course_object: courses.models.Course
    """

    # Update deadline job
    if course_object.deadline and (str(course_object.courseId) + 'assignment_check') not in main_scheduler.jobs:
        main_scheduler.add_deadline_notification(course_object.courseId)
    elif not course_object.deadline and (str(course_object.courseId) + 'assignment_check') in main_scheduler.jobs:
        main_scheduler.remove_deadline_notification(course_object.courseId)
    elif course_object.deadline and (str(course_object.courseId) + 'assignment_check') in main_scheduler.jobs:
        main_scheduler.remove_deadline_notification(course_object.courseId)
        main_scheduler.add_deadline_notification(course_object.courseId)

    # Update inactivity job
    if course_object.inactivity and (str(course_object.courseId) + 'inactive') not in main_scheduler.jobs:
        main_scheduler.add_inactivity_notification(course_object.courseId, course_object.inactivity_time)
    elif not course_object.inactivity and (str(course_object.courseId) + 'inactive') in main_scheduler.jobs:
        main_scheduler.remove_inactivity_notification(course_object.courseId)
    elif course_object.inactivity and (str(course_object.courseId) + 'inactive') in main_scheduler.jobs:
        main_scheduler.remove_inactivity_notification(course_object.courseId)
        main_scheduler.add_inactivity_notification(course_object.courseId, course_object.inactivity_time)


def on_delete_course(course_object):
    """
    Deletes all jobs of a course.

    :param course_object: modified Course object of which jobs need to be modified accordingly.
    :type course_object: courses.models.Course
    """

    if str(course_object.courseId) + 'assignment_check' in main_scheduler.jobs:
        main_scheduler.remove_deadline_notification(course_object.courseId)
    if str(course_object.courseId) + 'inactive' in main_scheduler.jobs:
        main_scheduler.remove_inactivity_notification(course_object.courseId)


def init_course_scheduler():
    """
    As this function is called on class init, we need to check if the migrations have been applied.
    This will fail during the [manage.py makemigrations, migrate] commands as these commands are creating the table.
    This prevents courses.models.Course modifications while the tables are still being made.
    """

    if 'scheduler_cronjob' not in connection.introspection.table_names():
        return
    course_models.COURSE_SCHEDULER_EVENT_ON_SAVE = on_save_course
    course_models.COURSE_SCHEDULER_EVENT_ON_DELETE = on_delete_course


# Enable course scheduler on Course.save() and Course.delete()
init_course_scheduler()
