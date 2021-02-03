# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Contains all database models."""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.template import loader
from django.conf import settings
import lib.ll_get_parsers
from courses.models import Course, Quiz
from . import learning_locker  # Leave the naming as is
from smart_selects.db_fields import ChainedForeignKey


# Create your models here.
class Assistant(models.Model):
    """Defines an assistant."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    forwarder_id = models.CharField(default=0, max_length=25)
    name = ''
    event = ''
    query_template = 'assistants/query.json'
    context = {}

    def __str__(self):
        return self.course.name

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Create or update the statement forwarder when assistant is created or updated."""
        self.context['course_id'] = self.course.courseId
        self.context['event'] = self.event
        self.context['moodle_base_url'] = settings.MOODLE_BASE_URL
        self.context['moodle_base_ip'] = settings.MOODLE_BASE_IP
        if not self.id:
            super(Assistant, self).save(*args, **kwargs)

            query = loader.render_to_string(self.query_template, self.context)
            self.create_statement_forwarder(query)
            if 'force_insert' in kwargs:
                del kwargs['force_insert']
            super(Assistant, self).save(*args, **kwargs)

        else:
            query = loader.render_to_string(self.query_template, self.context)
            try:
                learning_locker.update_statement_forwarder(self.forwarder_id, query)
            except learning_locker.LearningLockerException:
                self.create_statement_forwarder(query)
            super(Assistant, self).save(*args, **kwargs)

    def create_statement_forwarder(self, query):
        """
        Create the statement forwarder in Learning Locker and save the id into the database.

        :param query: Query of the statement forwarder.
        :type query: str
        """
        forwarder_id = lib.ll_get_parsers.parse_statement_forwarder_id(
            learning_locker.create_statement_forwarder(self.name, self.id, query))
        self.forwarder_id = forwarder_id

    def delete(self, *args, **kwargs):
        """Delete the statement forwarder when Action is deleted."""
        success = True
        try:
            learning_locker.delete_statement_forwarder(self.forwarder_id)
        except learning_locker.LearningLockerException:
            success = False
        finally:
            super(Assistant, self).delete(*args, **kwargs)
            return success


class NewActivityCreated(Assistant):
    """Defines the actions of sending a notification when new activities are added."""
    course = models.OneToOneField(Course, on_delete=models.CASCADE)
    name = 'new_activity_notification'
    event = "http://activitystrea.ms/schema/1.0/create"

    class Meta:
        verbose_name = "new activity assistant"


class QuizCompletedFeedback(Assistant):
    """Defines the actions of sending feedback when a student has completed a quiz."""

    quiz = ChainedForeignKey(Quiz,
                             chained_field="course",
                             chained_model_field="course",
                             show_all=False,
                             auto_choose=True,
                             sort=True)
    name = 'quiz_completed_feedback'
    event = "http://adlnet.gov/expapi/verbs/completed"
    question_feedback = models.BooleanField(verbose_name='Feedback on individual questions', default=False)
    threshold = models.IntegerField(verbose_name='threshold for quiz feedback', default=55,
                                    help_text='If a student scores below this threshold, he/she will receive feedback.'
                                              ' Enter a value between 0 and 100. The score is in percentages.',
                                    validators=[MinValueValidator(0), MaxValueValidator(100)])

    def save(self, *args, **kwargs):
        """Use the save function inherited from Assistant but alter two variables."""
        self.context['quiz_id'] = str(self.quiz.external_id)
        self.query_template = 'assistants/quiz_completed_query.json'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "quiz completed feedback assistant"


def build_new_activity_notification(course_name, activity_name, activity_type):
    """
    Build the notification message with the variables from the JSON response.

    :param activity_type: The type of the activity. Either quiz or assignment.
    :type activity_type: str
    :param course_name: The name of the course the activity is added to.
    :type course_name: str
    :param activity_name: The name of the new activity.
    :type activity_name: str
    :return: The message that will be send.
    :rtype: str
    """
    message = f'For the course {course_name} the {activity_type} {activity_name} is added.'
    return message
