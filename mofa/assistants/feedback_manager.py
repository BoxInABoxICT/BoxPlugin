# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""All the logic about giving feedback."""

from courses.models import Quiz, Resource, Question


def get_questions_feedback(params, questions):
    """
    Get the message that needs to be sent to the student, when they should receive question feedback.

    :param params: Info about the attempt.
    :type params: dict(str, str)
    :param question_feedback: Whether or not there needs to be feedback on specific questions.
    :type question_feedback: bool
    :param questions: Questions and whether they are answered correctly or not.
    :type questions: dict(int, dict(str, str))
    :return: The message that needs to be sent.
    :rtype: str
    """
    message = ''
    if False in questions.values():
        feedback_link = get_question_feedback_link(questions)
        message = build_completed_questions_feedback(
            params['actor_name'], params['quiz_name'],
            params['course_name'], params['score'] * 100, feedback_link)
    return message


def get_quiz_feedback(params, action):
    """
    Quiz feedback that needs to be sent to the student.

    :param params: Info about the students attempt.
    :type params: dict(str, str)
    :param action: The agents variables.
    :type action: Assistant
    :return: Message that needs to be sent to the Student.
    :rtype: str
    """
    threshold = action.threshold
    message = ''
    scale = 100
    if params['score'] < threshold / scale:
        feedback = get_quiz_feedback_link(params['quiz_id'])
        message = build_completed_quiz_feedback(params['actor_name'], params['quiz_name'],
                                                params['course_name'], params['score'] * scale, feedback)
    return message


def get_quiz_feedback_link(quiz_id):
    """
    Make a feedback string for the completed quiz feedback based on the content or subject linked to the quiz.

    :param quiz_id: Id from the quiz.
    :type quiz_id: int
    :return: A message that contains the feedback.
    :rtype: str
    """
    resources = Resource.objects.filter(quiz__external_id=quiz_id)
    subject = Quiz.objects.filter(external_id=quiz_id)[0].subjects_id
    # If a quiz is linked to Resource.
    if len(resources) != 0:
        name_content = resources[0].name
        target_content = resources[0].target
        link = f'<a href="{target_content}">{name_content}</a>'
    # If a quiz is linked to a Subject.
    elif subject is not None:
        link = ""
        content_array = Resource.objects.filter(subject__id=subject)
        # If no Resource is linked to the Subject.
        if len(content_array) == 0:
            link = "the course resource"
        # If Resource IS linked to the Subject.
        else:
            for resources in content_array:
                link += '\r\n- <a href="{}">{}</a>'.format(resources.target, resources.name)
    # If no Resource and no Subject is linked to a quiz.
    else:
        link = "the course resource"

    return link


def get_question_feedback_link(questions):
    """
    Generate the link that is sent to the student.

    :param questions: Attempt its questions and whether they are correctly answered or not.
    :type questions: dict(int, dict(str, str))
    :return: The message that needs to be sent, including HTML.
    :rtype: str
    """
    link = ['']
    for question in questions:
        # If question id's value is false:
        if not questions[question]:
            # If wrongly answered question has resources, get its name and target:
            if Question.objects.get(external_id=question).resources is not None:
                target_content = Question.objects.get(external_id=question).resources.target
                name_content = Question.objects.get(external_id=question).resources.name
                # If Resource is there, it always has a name. Check if it also has a target which can be linked to:
                if target_content is not None:
                    # If so, send a link to the target:
                    new_link = f'<p><a href="{target_content}">{name_content}</a></p>'
                else:
                    # Otherwise, just show the name:
                    new_link = f'<p> {name_content}</p>'
                if new_link not in link:
                    link.append(new_link)
            # If question has no Resource, check whether it has a subject and then do the same things as before:
            else:
                if not Question.objects.get(external_id=question).subjects is None:
                    subjects = Question.objects.get(external_id=question).subjects.resources.values_list('target',
                                                                                                         flat=True)
                    if not len(subjects) == 0:
                        for i in range(len(subjects)):
                            content_targets = subjects[i]
                            content_name = (Question.objects.get(external_id=question).subjects.resources.
                                            values_list('name', flat=True)[i])
                            if content_targets is not None:
                                new_link = f'<p><a href="{content_targets}">{content_name}</a></p>'
                            else:
                                new_link = f'<p>{content_name}</p>'
                            if new_link not in link:
                                link.append(new_link)
    return ''.join(link)


def build_completed_quiz_feedback(actor_name, quiz_name, course_name, score, feedback):
    """
    Build the feedback when an user has completed the quiz and has failed the quiz.

    :param actor_name: Name of the user that has completed the quiz.
    :type actor_name: str
    :param quiz_name: Name of the quiz.
    :type quiz_name: str
    :param course_name: Name of the course.
    :type course_name: str
    :param score: Result of the user.
    :type score: int
    :param feedback: String with the feedback.
    :type feedback: str
    :return: String of the message.
    :rtype: str
    """
    message = f'Hi {actor_name},\n You have completed the quiz "{quiz_name}" for the course "{course_name}". ' \
              f'Your result was {score}%, which is below the threshold. It could be helpful to look at: ' \
              f'{feedback}'
    return message


def build_completed_questions_feedback(actor_name, quiz_name, course_name, score, feedback):
    """
    Build the feedback when an user has completed the quiz and has failed the quiz.

    :param actor_name: Name of the user that has completed the quiz.
    :type actor_name: str
    :param quiz_name: Name of the quiz.
    :type quiz_name: str
    :param course_name: Name of the course.
    :type course_name: str
    :param score: Result of the user.
    :type score: str
    :param feedback: String with the feedback.
    :type feedback: str
    :return: String of the message.
    :rtype: str
    """
    if feedback == '':
        return ''
    message = f'Hi {actor_name},\n You have completed the quiz "{quiz_name}" for the course "{course_name}". ' \
              f'You did not answer every question correct. For information about the topics of the questions ' \
              f'you answered wrong, please take a look at: {feedback}'
    return message
