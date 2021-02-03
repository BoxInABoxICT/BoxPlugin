# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Add models to interface."""
from django.contrib import admin, messages

from assistants import learning_locker
from . import models


class AssistantAdmin(admin.ModelAdmin):
    """Abstract class that filter queryset and checks permissions."""

    list_display = ('course', 'warnings')
    exclude = ('forwarder_id',)

    def get_queryset(self, request):
        """
        Filter queryset to only show assistants the user has access to.

        :param request: The get_queryset request.
        :type request: WSGIRequest
        :return: All the assistants a user has access to.
        :rtype: QuerySet
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(course__in=request.user.courses.all())

    def has_view_or_change_permission(self, request, obj=None):
        """
        Restrict the user from viewing/changing assistants the user has access to.

        :param request: The has_view_or_change_permission request.
        :type request: WSGIRequest
        :param obj: The Assistant object.
        :type obj: Assistant
        :return: Whether this user can access this Assistant.
        :rtype: QuerySet
        """
        if request.user.is_superuser:
            return True
        courses = request.user.courses.all()
        if obj is not None:
            return obj.course in courses
        else:
            return True

    def has_add_permission(self, request):
        """
        Restrict the user from adding an Assistant if no permission was given.

        :param request: The has_add_permission request.
        :type request: WSGIRequest
        :return: Whether the user has add permissions or not.
        :rtype: bool
        """
        if request.user.is_superuser:
            return True
        courses = request.user.courses.all()
        if len(courses) == 0:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        """
        Restrict the user from deleting this assistant if no permission was given.

        :param request: The has_delete_permission request.
        :type request: WSGIRequest
        :param obj: The Assistant.
        :type obj: Assistant
        :return: Whether the user has delete permissions or not.
        :rtype: bool
        """
        if request.user.is_superuser:
            return True
        courses = request.user.courses.all()
        if obj is not None:
            return obj.course in courses
        else:
            return True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filter the dropdown for choosing the course (based on the courses that the user can edit).

        :param db_field: The database field of the dropdown.
        :type db_field: database field
        :param request: The formfield_for_foreignkey request.
        :type request: WSGIRequest
        :return: The Assistants the user is allowed to see.
        :rtype: QuerySet
        """
        if db_field.name == 'course':
            if not request.user.is_superuser:
                kwargs['queryset'] = request.user.courses.all()
        return super(AssistantAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    @staticmethod
    def warnings(obj):
        """
        Add warnings to an assistant when there is no statement forwarder of the assistant in LL.

        :param obj: The Assistant object.
        :type obj: Assistant
        :return: A warning message.
        :rtype: str
        """
        if learning_locker.check_statement_forwarder(obj.forwarder_id):
            return ''
        else:
            return '⚠️This assistant has no statement forwarder in Learning Locker. ' \
                   'Save the assistant again to create a new statement forwarder. ⚠️'

    @staticmethod
    def has_error(obj):
        """
        Check whether or not the obj contains a broken statement forwarder.

        :param obj: The Assistant object.
        :type obj: Assistant
        :return: Whether or not the Assistant has an error.
        :rtype: bool
        """
        if obj is not None:
            return not learning_locker.check_statement_forwarder(obj.forwarder_id)
        else:
            return False

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """
        Override the render_change_form to add a warning when a statement forwarder is broken.

        :param request: The render_change_form request.
        :type request: WSGIRequest
        :param context: The context of the render_change_form context.
        :type context: str
        :param add: Add render_change_form parameter, default is false.
        :type add: bool
        :param change: Change render_change_form parameter,  default is false.
        :type change: bool
        :param form_url: The render_change_form url.
        :type form_url: str
        :param obj: The Assistant object.
        :type obj: Assistant
        :return: The form with possibly the warning message.
        :rtype: AssistantAdmin
        """
        """"""
        print(f"request:{type(request)}")
        print(f"context:{type(context)}")
        print(f"obj:{type(obj)}")
        if self.has_error(obj):
            self.message_user(request=request, level=messages.WARNING,
                              message='This assistant has no statement forwarder in Learning Locker. '
                                      'Save the assistant again to create a new statement forwarder.')
        return super(AssistantAdmin, self).render_change_form(request, context, add=add, change=not add, obj=obj,
                                                              form_url=form_url)


@admin.decorators.register(models.NewActivityCreated)
class NewActivityCreatedAdmin(AssistantAdmin):
    """Add new activity to admin interface."""

    def delete_queryset(self, request, queryset):
        """
        Override bulk delete function. Also deletes the LL Forwarders.

        :param request: The delete_queryset request.
        :type request: WSGIRequest
        :param queryset: All New Activity Assistants.
        :type queryset: QuerySet
        """
        for query in queryset:
            models.NewActivityCreated.delete(query)


@admin.decorators.register(models.QuizCompletedFeedback)
class QuizCompletedFeedbackAdmin(AssistantAdmin):
    """Add feedback for quiz to admin interface."""

    def delete_queryset(self, request, queryset):
        """
        Override bulk delete function. Also deletes the LL Forwarders.

        :param request: The delete_queryset request.
        :type request: WSGIRequest
        :param queryset: All Quiz Completed Feedback Assistants.
        :type queryset: QuerySet
        """
        for query in queryset:
            models.QuizCompletedFeedback.delete(query)
