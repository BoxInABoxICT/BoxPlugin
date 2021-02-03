# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Add models to interface."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.forms import ModelForm

from courses.models import Resource, Question, Subject
from scheduler import deadline_manager, inactivity_courses, main_scheduler
from . import models
from .models import User


class UserAdmin(BaseUserAdmin):
    """Add moodle id to the User Admin interface."""

    BaseUserAdmin.fieldsets[0][1]['fields'] = ('username', 'password', 'moodle_id')


admin.site.register(User, UserAdmin)


def manual_inactivity(modeladmin, request, queryset):
    """
    Add an option to manually check the inactivity.

    :param modeladmin: Representation of a model in the admin interface. Not being used.
    :type modeladmin: CourseAdmin
    :param request: HttpRequest representing the current request. Not being used.
    :type request: WSGIRequest
    :param queryset: Class containing the set of objects selected by the user.
    :type queryset: QuerySet
    """
    for query in queryset:
        inactivity_courses.create_job(query.courseId, query.inactivity_time, main_scheduler.main_scheduler)


manual_inactivity.short_description = "Perform inactivity check."
"Description that is displayed in the user interface"


def manual_deadline(modeladmin, request, queryset):
    """
    Add an option to manually check the deadlines.

    :param modeladmin: Representation of a model in the admin interface. Not being used.
    :type modeladmin: CourseAdmin
    :param request: HttpRequest representing the current request. Not being used.
    :type request: WSGIRequest
    :param queryset: Class containing the set of objects selected by the user.
    :type queryset: QuerySet
    """
    for query in queryset:
        deadline_manager.notify_about_upcoming_deadlines(query.courseId, query.hours_before * 3600)


manual_deadline.short_description = "Perform upcoming deadline check."
"Description that is displayed in the user interface"


class ResourceInline(admin.TabularInline):
    """Create the horizontal resource layout for the internal resource."""

    def get_queryset(self, request):
        """
        Overwrite the standard get_queryset function, to only select the resources that are internal.

        :param request: The get_queryset request. Not being used.
        :type request: WSGIRequest
        :return: All the resources that are internal.
        :rtype: QuerySet
        """
        qs = super(ResourceInline, self).get_queryset(request)
        return qs.filter(external=False)

    def has_change_permission(self, request, obj=None):
        """
        Overwrite the standard has_change_permission function, to make it read-only.

        :param request: The has_change_permission request. Not being used.
        :type request: WSGIRequest
        :param obj: The Course object. Not being used.
        :type obj: Course
        :return: False, everything here is read-only.
        :rtype: bool
        """
        return False

    def has_add_permission(self, request, obj=None):
        """
        Overwrite the standard has_add_permission function, to remove add resource button.

        :param request: The has_add_permission request. Not being used.
        :type request: WSGIRequest
        :param obj: The Course object. Not being used.
        :type obj: Course
        :return: False, no objects should be added, since they are loaded from Moodle.
        :rtype: bool
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Overwrite the standard has_delete_permission function, to remove delete resource button.

        :param request: The has_delete_permission request. Not being used.
        :type request: WSGIRequest
        :param obj: The Course object. Not being used.
        :type obj: Course
        :return: False, nothing should be deleted from Mofa since it is loaded from Moodle.
        :rtype: bool
        """
        return False

    exclude = ['external', 'external_id']
    ordering = ('target',)
    model = Resource
    extra = 0
    verbose_name_plural = "Imported Resources (cannot be edited)"


class ResourceInlineExternal(admin.TabularInline):
    """Create the horizontal resource layout for external resource."""

    def get_queryset(self, request):
        """
        Overwrite the standard get_queryset function, to only select the resources that are external.

        :param request: The get_queryset request.
        :type request: WSGIRequest
        :return: All the resources that are external.
        :rtype: QuerySet
        """
        qs = super(ResourceInlineExternal, self).get_queryset(request)
        return qs.filter(external=True)

    exclude = ['external', 'external_id']
    model = Resource
    extra = 0
    verbose_name_plural = "External Resources (may be edited)"


class ResourceSubjForm(ModelForm):
    """Create resource form and sort them alphabetically."""

    def __init__(self, *args, **kwargs):
        """Sort the resources by name, filter resources to match the course. Do the same for subjects."""
        super(ResourceSubjForm, self).__init__(*args, **kwargs)
        self.fields['resources'].queryset = Resource.objects.order_by('name')
        self.fields['resources'].queryset = Resource.objects.filter(course_id=self.instance.course.id)
        self.fields['subjects'].queryset = Subject.objects.order_by('name')
        self.fields['subjects'].queryset = Subject.objects.filter(course_id=self.instance.course.id)

    class Meta:
        model = models.Assessment
        exclude = []


class QuestionForm(ModelForm):
    """Display only the resources of the course of the quiz questions."""

    def __init__(self, *args, **kwargs):
        """Filter the resources of the corresponding course."""
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields['resources'].queryset = Resource.objects.order_by('name')
        self.fields['resources'].queryset = Resource.objects.filter(course_id=self.instance.course_id)
        self.fields['subjects'].queryset = Subject.objects.order_by('name')
        self.fields['subjects'].queryset = Subject.objects.filter(course_id=self.instance.course_id)

    class Meta:
        model = models.Question
        exclude = []


class QuestionInline(admin.TabularInline):
    """Create questions horizontal layout."""

    def has_add_permission(self, request, obj=None):
        """
        Overwrite the standard has_add_permission function, to remove add content button.

        :param request: The has_add_permission request.
        :type request: WSGIRequest
        :param obj: The Question object. Not being used.
        :type obj: Question
        :return: False, no objects should be added, since they are loaded from Moodle.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Overwrite the standard has_delete_permission function, to remove delete content button.

        :param request: The has_delete_permission request.
        :type request: WSGIRequest
        :param obj: The Question object. Not being used.
        :type obj: Question
        :return: False, nothing should be deleted from Mofa since it is loaded from Moodle.
        """
        return False

    model = Question
    extra = 0
    exclude = ('course', 'external_id')
    readonly_fields = ('name',)
    fields = ('name', 'subjects', 'resources',)
    form = QuestionForm


class AssessmentAdmin(admin.ModelAdmin):
    """Abstract class that filter queryset and checks permissions."""

    def get_queryset(self, request):
        """
        Filter queryset to only show assessments the user has access to.

        :param request: The get_queryset request.
        :type request: WSGIRequest
        :return: All the assessments a user has access to.
        :rtype: QuerySet
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(course__in=request.user.courses.all())

    def has_view_or_change_permission(self, request, obj=None):
        """
        Restrict the user from viewing/changing assessments the user has access to.

        :param request: The has_view_or_change_permission request.
        :type request: WSGIRequest
        :param obj: The Assessment object
        :type obj: Assessment
        :return: Whether this user can access this Assessment.
        :rtype: QuerySet
        """
        if request.user.is_superuser:
            return True
        courses = request.user.courses.all()
        if obj is not None:
            return courses.filter(courseId=obj.course.courseId).exists()
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        """Restrict the user from deleting this assistant if no permission was given."""
        if request.user.is_superuser:
            return True
        else:
            False

    def has_add_permission(self, request):
        """
        Set add permission on false. Assessments are loaded from Moodle, should not be added manually.

        :param request: The add_permission request.
        :type request: WSGIRequest
        :return: False, disable add permissions.
        :rtype: bool
        """
        return False

    class Meta:
        abstract = True

    exclude = ['course', 'external_id']
    readonly_fields = ('name',)
    fields = ('name', 'subjects', 'resources')


@admin.decorators.register(models.Quiz)
class QuizAdmin(AssessmentAdmin):
    """Admin page for quizzes."""

    form = ResourceSubjForm
    fields = ('name', 'course', 'subjects', 'resources')
    readonly_fields = ('name', 'course',)
    list_display = ('__str__', 'course',)
    inlines = [QuestionInline]

    class Media:
        """Include extra css."""

        css = {
            'all': ('css/inline_override.css',)
        }


@admin.decorators.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    """Whitelist the parameters shown in the admin panel. Add the manual actions."""

    list_display = ('name', 'courseId', 'inactivity', 'platform', 'deadline')
    actions = [manual_deadline, manual_inactivity]
    inlines = [ResourceInline, ResourceInlineExternal]
    readonly_fields = ('name', 'courseId', 'platform')

    def delete_queryset(self, request, queryset):
        """
        Call delete on every course individually when deleting multiple courses.

        :param request: The delete_queryset request.
        :type request: WSGIRequest
        :param queryset: All selected courses
        :type queryset: QuerySet
        """
        for course in queryset:
            course.delete()
        super(CourseAdmin, self).delete_queryset(request, queryset)

    fieldsets = (
        (None, {
            'fields': ('name', 'platform', 'courseId')
        }),
        ('Inactivity', {
            'fields': ('inactivity', 'inactivity_time')
        }),
        ('Deadline', {
            'fields': ('deadline', 'hours_before')
        })
    )

    class Media:
        """Include extra css."""

        css = {
            'all': ('css/inline_override.css',)
        }

    def has_view_or_change_permission(self, request, obj=None):
        """
        Restrict the user from viewing/changing courses the user has access to.

        :param request: The has_view_or_change_permission request.
        :type request: WSGIRequest
        :param obj: The course object.
        :type obj: Course
        :return: Whether this user can access this Course.
        :rtype: bool

        """
        if request.user.is_superuser:
            return True
        courses = request.user.courses.all()
        if obj is not None:
            return courses.filter(courseId=obj.courseId).exists()
        else:
            return True

    def get_queryset(self, request):
        """
        Filter queryset to only show courses the user has access to.

        :param request: The get_queryset request.
        :type request: WSGIRequest
        :return: All courses a user has access to.
        :rtype: QuerySet
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(pk__in=request.user.courses.all())

    def has_add_permission(self, request):
        """
        Set add_permission on false. Courses are loaded from Moodle, should not be added manually.

        :param request: The add_permission request.
        :type request: WSGIRequest
        :return: False, disable add permissions.
        :rtype: bool
        """
        return False


@admin.decorators.register(models.Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin page for subjects."""

    list_display = ('__str__', 'course', 'warnings',)

    def get_queryset(self, request):
        """Filter queryset to only show subjects the user has access to.

        :param request: The get_queryset request.
        :type request: WSGIRequestf
        :return: QuerySet filter on whether a user has access to this subject.
        :rtype: QuerySet
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(course__in=request.user.courses.all())

    def has_view_or_change_permission(self, request, obj=None):
        """
        Restrict the user from viewing/changing this subject if no permission was given.

        :param request: The has_view_or_change_permission request.
        :type request: WSGIRequest
        :return: Bool whether or not a user can access the subject.
        :rtype: bool
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
        Restrict the user from adding an subject if no permission was given.

        :param request: The has_add_permission request.
        :type request: WSGIRequest
        :return: Bool whether or not a user can add a new subject.
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
        Restrict the user from deleting this subject if no permission was given.

        :param request: The has_delete_permission request.
        :type request: WSGIRequest
        :return: Bool whether or not a user can delete a subject.
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

        :param request: The formfield_for_foreignkey request.
        :type request: WSGIRequest
        :param db_field: The db_field of the dropdown menu.
        :type db_field: QuerySet
        :return: QuerySet for corresponding dropdown menu.
        :rtype: QuerySet

        """
        if db_field.name == 'course':
            if not request.user.is_superuser:
                kwargs['queryset'] = request.user.courses.all()
        return super(SubjectAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    @staticmethod
    def warnings(obj):
        """
        Add warnings to an subject when there is no statement forwarder of the assistant in LL.

        :param obj: The subject object.
        :type obj: Subject
        :return: A warning when a subject has no resource.
        :rtype: str
        """
        if obj.resources.count() > 0:
            return ''
        else:
            return 'This subject contains no resources!'


@admin.decorators.register(models.Assignment)
class AssignmentAdmin(AssessmentAdmin):
    """Admin page for assignment."""

    form = ResourceSubjForm
    fields = ('name', 'course', 'subjects', 'resources')
    readonly_fields = ('name', 'course',)
    list_display = ('__str__', 'course',)


@admin.decorators.register(models.Choice)
class ChoiceAdmin(AssessmentAdmin):
    """Admin page for assignment."""

    form = ResourceSubjForm
    fields = ('name', 'course', 'subjects', 'resources')
    readonly_fields = ('name', 'course',)
    list_display = ('__str__', 'course',)
