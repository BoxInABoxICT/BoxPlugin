# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Contains test data."""
test_logger_contains_error_message = \
    {
        "exception": "invalid_parameter_exception",
        "errorcode": "invalidparameter",
        "message": "Invalid parameter value detected"
    }

test_logger_contains_no_error = \
    {
        "id": 4,
        "username": "WS",
        "firstname": "Will",
        "lastname": "Smith",
        "fullname": "Will Smith",
        "email": "Will_Smith@email.com",
        "department": "",
        "firstaccess": 1571915496,
        "lastaccess": 1573741592,
        "lastcourseaccess": 1572953180,
        "description": "",
        "descriptionformat": 1,
        "profileimageurlsmall": "http://localhost:4000/theme/image.php/boost/core/1571136560/u/f2",
        "profileimageurl": "http://localhost:4000/theme/image.php/boost/core/1571136560/u/f1",
        "groups": [],
        "roles": [
            {
                "roleid": 5,
                "name": "",
                "shortname": "student",
                "sortorder": 0
            }
        ],
        "enrolledcourses": [
            {
                "id": 2,
                "fullname": "Python tutorial",
                "shortname": "pytut"
            }
        ]
    }

test_parse_quiz_question_answered_data = \
    {
        "statement": {
            "actor": {
                "name": "Will Smith",
                "account": {
                    "name": "3"
                }
            },
            "result": {
                "response": "True",
                "completion": True,
                "success": False
            },
            "object": {
                "definition": {
                    "name": {
                        "en": "Test Test"
                    }
                }
            }
        }
    }

test_parse_quiz_completed_feedback = \
    {
        "statement": {
            "actor": {
                "name": "Will Smith",
                "account": {
                    "name": "3"
                }
            },
            "result": {
                "score": {
                    "scaled": 0
                }
            },
            "object": {
                "definition": {
                    "name": {
                        "en": "Testquiz1"
                    }
                },
                "id": "http://localhost:4000/mod/quiz/view.php?id=18"
            },
            "context": {
                "contextActivities": {
                    "grouping": [
                        {
                        },
                        {
                            "id": "http://localhost:4000/course/view.php?id=2",
                            "definition": {
                                "name": {
                                    "en": "BeginningCourse"
                                }
                            }
                        }
                    ],
                    "other": [
                        {"id": "http://localhost:4000/mod/quiz/attempt.php?attempt=107&cmid=11"}
                    ]
                }
            },
            "id": "Dummy-id"
        }
    }

test_parse_send_message_data = \
    {
        "activities": [
            "http://localhost:4000/course/view.php?id=2"
        ],
        "statement": {
            "actor": {
                "name": "Will Smith",
                "account": {
                    "name": "3"
                }
            },
            "context": {
                "platform": "Moodle"
            },
            "object": {
                "definition": {
                    "name": {
                        "en": "Test Test"
                    }
                }
            }
        }
    }

test_moodle_send_message_return = \
    [
        {
            "msgid": 63,
            "text": "<p>Awesome!</p>",
            "timecreated": 1573811762,
            "conversationid": 4,
            "useridfrom": 3,
            "candeletemessagesforallusers": True
        }
    ]

test_moodle_course_by_id_field_return = \
    {
        "courses": [
            {
                "id": 2,
                "fullname": "Python tutorial",
                "displayname": "Python tutorial",
                "shortname": "pytut",
                "categoryid": 1,
                "categoryname": "Miscellaneous",
                "sortorder": 10005,
                "summary": "<p>Learning python like a boss</p>",
                "summaryformat": 1,
                "summaryfiles": [],
                "overviewfiles": [],
                "contacts": [],
                "enrollmentmethods": [
                    "manual"
                ],
                "idnumber": "",
                "format": "topics",
                "showgrades": 1,
                "newsitems": 5,
                "startdate": 1571180400,
                "enddate": 1602716400,
                "maxbytes": 0,
                "showreports": 0,
                "visible": 1,
                "groupmode": 0,
                "groupmodeforce": 0,
                "defaultgroupingid": 0,
                "enablecompletion": 1,
                "completionnotify": 0,
                "timecreated": 1571136683,
                "timemodified": 1571136683,
                "requested": 0,
                "cacherev": 1573740452,
                "filters": [
                    {
                        "filter": "mathjaxloader",
                        "localstate": 0,
                        "inheritedstate": 1
                    },
                    {
                        "filter": "activitynames",
                        "localstate": 0,
                        "inheritedstate": 1
                    },
                    {
                        "filter": "mediaplugin",
                        "localstate": 0,
                        "inheritedstate": 1
                    }
                ],
                "courseformatoptions": [
                    {
                        "name": "hiddensections",
                        "value": 0
                    },
                    {
                        "name": "coursedisplay",
                        "value": 0
                    }
                ]
            }
        ],
        "warnings": []
    }

test_moodle_get_messages_return = \
    {
        "messages": [
            {
                "id": 74,
                "useridfrom": 2,
                "useridto": 4,
                "subject": "New message from Admin User",
                "text": "<p>Hello Mr. Smith</p>",
                "fullmessage": "Hello Mr. Smith",
                "fullmessageformat": 0,
                "fullmessagehtml": "",
                "smallmessage": "Hello Mr. Smith",
                "notification": 0,
                "contexturl": "",
                "contexturlname": "",
                "timecreated": 1573830472,
                "timeread": None,
                "usertofullname": "Hello Mr. Smith",
                "userfromfullname": "Admin User",
                "customdata": "{\"notificationiconurl\":\"http:\\/\\/localhost:4000\\/theme\\/image.php\\/boost\\/core"
                              "\\/1571136560\\/u\\/f2\",\"actionbuttons\":{\"send\":\"Send\"},\"placeholders\":{\"send"
                              "\":\"Write a message...\"},\"courseid\":1}"
            }
        ],
        "warnings": []
    }

test_moodle_get_assignments_return = \
    {
        "courses": [
            {
                "assignments": [
                    {
                        "cmid": 6,
                        "name": "Learning basic loops",
                        "duedate": 1573776060,
                    },
                    {
                        "cmid": 9,
                        "name": "Learning booleans",
                        "duedate": 1573776060,
                    },
                ]
            }
        ],
        "warnings": []
    }

test_moodle_get_assignments_status_return = \
    [
        {
            "cmid": 6,
            "name": "Learning basic loops",
            "duedate": 1573776060,
        },
        {
            "cmid": 9,
            "name": "Learning booleans",
            "duedate": 1573776060,
        },
    ]

test_database_create_resource = \
    {'courseId': 2, 'verb': 'created', 'target': 'http://localhost:4000/mod/book/view.php?id=13',
     'type': 'book', 'name': 'Advanced Python', 'parent': None, 'external_id': 13, 'actor_id': 2}

test_database_update_resource = \
    {'courseId': 2, 'verb': 'created', 'target': 'http://localhost:4000/mod/book/view.php?id=13',
     'type': 'book', 'name': 'Advanced', 'parent': None, 'external_id': 13, 'actor_id': 2}

test_database_create_assign = \
    {'courseId': 2, 'verb': 'created', 'target': 'http://localhost:4000/mod/assign/view.php?id=10',
     'type': 'assign', 'name': 'For loops', 'parent': None, 'external_id': 10, 'actor_id': 2}

test_database_update_assign = \
    {'courseId': 2, 'verb': 'created', 'target': 'http://localhost:4000/mod/assign/view.php?id=10',
     'type': 'assign', 'name': 'For Loops', 'parent': None, 'external_id': 10, 'actor_id': 2}

test_database_create_quiz = \
    {'courseId': 2, 'verb': 'created', 'target': 'http://localhost:4000/mod/quiz/view.php?id=10',
     'type': 'quiz', 'name': 'For loops', 'parent': None, 'external_id': 10, 'actor_id': 2}

test_database_update_quiz = \
    {'courseId': 2, 'verb': 'created', 'target': 'http://localhost:4000/mod/quiz/view.php?id=10',
     'type': 'quiz', 'name': 'For', 'parent': None, 'external_id': 10, 'actor_id': 2}

test_database_create_choice = \
    {'courseId': 2, 'verb': 'created', 'target': 'http://localhost:4000/mod/choice/view.php?id=10',
     'type': 'choice', 'name': 'For loops', 'parent': None, 'external_id': 10, 'actor_id': 2}

test_database_update_choice = \
    {'courseId': 2, 'verb': 'created', 'target': 'http://localhost:4000/mod/choice/view.php?id=10',
     'type': 'choice', 'name': 'F', 'parent': None, 'external_id': 10, 'actor_id': 2}

test_database_create_course = \
    {
        'courseId': 3, 'platform': 'Moodle', 'course_name': 'Python Tutorial', 'verb': 'created', 'actor_id': 2
    }

test_database_update_course = \
    {
        'courseId': 3, 'platform': 'Moodle', 'course_name': 'Python', 'verb': 'created', 'actor_id': 2
    }

test_build_sync_agent_get_data = \
    {
        "edges": [
            {
                "node": {
                    "_id": "1234"
                }
            }
        ]
    }

test_build_sync_agent_get_data_empty = \
    {
        "edges": []
    }

test_get_questions = {'8': False, '9': True}

test_get_questions2 = {'8': True, '9': False}

test_database_assign_user = \
    {
        'role': 'editingteacher', 'course_id': '2', 'firstname': 'Test', 'lastname': 'User', 'username': 'test_user',
        'email': 'test@test.nl', 'id': '3'
    }

test_database_unassign_user = \
    {
        'role': 'editingteacher', 'course_id': '2', 'user_id': '3'
    }

test_database_deleted_user = \
    {
        'user_id': '3'
    }

test_database_updated_user = \
    {
        'firstname': 'Test', 'lastname': 'Usertje', 'username': 'test_user', 'email': 'test@test.nl', 'id': '3'
    }

test_get_statement_forwarders = \
    [
        {
            "configuration": {
                "url": f"DUMMY_DJANGO_URL:1234/assistants/api/user_sync_agent/",
                "maxRetries": 10
            },
            "_id": "5e18457334e93be8d0c6c923",
            "organisation": "5da5a35280180f001d62494b",
        },
        {
            "configuration": {
                "protocol": "http",
                "authType": "no auth",
                "url": f"DUMMY_DJANGO_URL:1234/assistants/api/quiz_completed_feedback/2/",
                "maxRetries": 10
            },
            "_id": "5e1849cc34e93b75adc6c92d",
            "organisation": "5da5a35280180f001d62494b",
        }
    ]

test_get_statement_forwarders_delete = \
    [
        {
            "configuration": {
                "url": f"DUMMY_DJANGO_URL:1234/assistants/api/course_sync_agent/",
                "maxRetries": 10
            },
            "_id": "5e18457334e93be8d0c6c923",
            "organisation": "5da5a35280180f001d62494b",
        },
        {
            "configuration": {
                "url": f"DUMMY_DJANGO_URL:1234/assistants/api/quiz_completed_feedback/2/",
                "maxRetries": 10
            },
            "_id": "5e1849cc34e93b75adc6c92d",
            "organisation": "5da5a35280180f001d62494b",
        },
        {
            "configuration": {
                "url": f"DUMMY_DJANGO_URL:1234/assistants/api/quiz_completed_feedback/3/",
                "maxRetries": 10
            },
            "_id": "5e1849cc34e93b75adc6c92e",
            "organisation": "5da5a35280180f001d62494b",
        }
    ]

test_question_create = \
    {
        'course_id': '2', 'quiz_id': '52',
        'questions': [
            {
                'question_id': '4',
                'question_name': 'Do loops loop',
                'question_text': '<p>Loops loop but do they?</p>'
            }
        ]
    }

test_question_update = \
    {
        'course_id': '2', 'quiz_id': '52',
        'questions': [
            {
                'question_id': '4',
                'question_name': 'Do loops loop',
                'question_text': '<p>Loops loop but do they?</p>'
            },
            {
                "question_id": "5",
                "question_name": "Loopdieloop",
                "question_text": "<p>Loopdieloop?</p>"
            }
        ]
    }

test_question_delete = \
    {
        'course_id': '2', 'quiz_id': '52',
        'questions': []
    }
