# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Contains test data."""

test_get_assignments_data = \
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

test_get_assignments_check = \
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

test_assignment_completion_check = \
    {
        "statuses": [
            {
                "cmid": 6,
                "state": 1
            },
            {
                "cmid": 9,
                "state": 0
            }
        ],
        "warnings": []
    }

test_get_enrolled_users = \
    [
        {
            "id": 4,
            "username": "WS",
            "firstname": "Will",
            "lastname": "Smith",
            "fullname": "Will Smith",
        }
    ]

test_inactivity_get_enrolled_users = \
    [
        {
            "id": 2
        },
        {
            "id": 3
        },
        {
            "id": 4
        },
        {
            "id": 5
        }
    ]

test_get_courses_by_id = \
    {
        'courses': [
            {
                'id': 2,
                'fullname': 'BeginningCourse'
            }
        ]
    }

test_get_courses_by_id_ended = \
    {
        'courses': [
            {
                'id': 2,
                'fullname': 'No view course',
                'displayname': 'No view course',
                'shortname': 'nvc',
                'categoryid': 1,
                'categoryname': 'Miscellaneous',
                'sortorder': 10001,
                'summary': '',
                'summaryformat': 1,
                'summaryfiles': [],
                'overviewfiles': [],
                'contacts': [
                    {'id': 4,
                     'fullname': 'Saskia Restful Notificaties'}],
                'enrollmentmethods': ['manual'],
                'idnumber': '',
                'format': 'topics',
                'showgrades': 1,
                'newsitems': 5,
                'startdate': 1605740400,
                'enddate': 1637276800,
                'maxbytes': 0,
                'showreports': 0,
                'visible': 1,
                'groupmode': 0,
                'groupmodeforce': 0,
                'defaultgroupingid': 0,
                'enablecompletion': 1,
                'completionnotify': 0,
                'lang': '',
                'theme': '',
                'marker': 0,
                'legacyfiles': 0,
                'calendartype': '',
                'timecreated': 1605708824,
                'timemodified': 1605708824,
                'requested': 0,
                'cacherev': 1605801045,
                'filters': [{'filter': 'displayh5p', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'activitynames', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'mathjaxloader', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'emoticon', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'urltolink', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'mediaplugin', 'localstate': 0, 'inheritedstate': 1}],
                'courseformatoptions': [{'name': 'hiddensections', 'value': 0},
                                        {'name': 'coursedisplay', 'value': 0}]}]
    }

test_get_courses_by_id_live = \
    {
        'courses': [
            {
                'id': 2,
                'fullname': 'No view course',
                'displayname': 'No view course',
                'shortname': 'nvc',
                'categoryid': 1,
                'categoryname': 'Miscellaneous',
                'sortorder': 10001,
                'summary': '',
                'summaryformat': 1,
                'summaryfiles': [],
                'overviewfiles': [],
                'contacts': [
                    {'id': 4,
                     'fullname': 'Saskia Restful Notificaties'}],
                'enrollmentmethods': ['manual'],
                'idnumber': '',
                'format': 'topics',
                'showgrades': 1,
                'newsitems': 5,
                'startdate': 1605740400,
                'enddate': 1637276400,
                'maxbytes': 0,
                'showreports': 0,
                'visible': 1,
                'groupmode': 0,
                'groupmodeforce': 0,
                'defaultgroupingid': 0,
                'enablecompletion': 1,
                'completionnotify': 0,
                'lang': '',
                'theme': '',
                'marker': 0,
                'legacyfiles': 0,
                'calendartype': '',
                'timecreated': 1605708824,
                'timemodified': 1605708824,
                'requested': 0,
                'cacherev': 1605801045,
                'filters': [{'filter': 'displayh5p', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'activitynames', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'mathjaxloader', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'emoticon', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'urltolink', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'mediaplugin', 'localstate': 0, 'inheritedstate': 1}],
                'courseformatoptions': [{'name': 'hiddensections', 'value': 0},
                                        {'name': 'coursedisplay', 'value': 0}]}]
    }

test_get_courses_by_id_young = \
    {
        'courses': [
            {
                'id': 2,
                'fullname': 'No view course',
                'displayname': 'No view course',
                'shortname': 'nvc',
                'categoryid': 1,
                'categoryname': 'Miscellaneous',
                'sortorder': 10001,
                'summary': '',
                'summaryformat': 1,
                'summaryfiles': [],
                'overviewfiles': [],
                'contacts': [
                    {'id': 4,
                     'fullname': 'Saskia Restful Notificaties'}],
                'enrollmentmethods': ['manual'],
                'idnumber': '',
                'format': 'topics',
                'showgrades': 1,
                'newsitems': 5,
                'startdate': 1605740400,
                'enddate': 1606487200,
                'maxbytes': 0,
                'showreports': 0,
                'visible': 1,
                'groupmode': 0,
                'groupmodeforce': 0,
                'defaultgroupingid': 0,
                'enablecompletion': 1,
                'completionnotify': 0,
                'lang': '',
                'theme': '',
                'marker': 0,
                'legacyfiles': 0,
                'calendartype': '',
                'timecreated': 1606400370,
                'timemodified': 1605708824,
                'requested': 0,
                'cacherev': 1605801045,
                'filters': [{'filter': 'displayh5p', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'activitynames', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'mathjaxloader', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'emoticon', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'urltolink', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'mediaplugin', 'localstate': 0, 'inheritedstate': 1}],
                'courseformatoptions': [{'name': 'hiddensections', 'value': 0},
                                        {'name': 'coursedisplay', 'value': 0}]}]
    }

test_get_courses_by_id_old = \
    {
        'courses': [
            {
                'id': 2,
                'fullname': 'No view course',
                'displayname': 'No view course',
                'shortname': 'nvc',
                'categoryid': 1,
                'categoryname': 'Miscellaneous',
                'sortorder': 10001,
                'summary': '',
                'summaryformat': 1,
                'summaryfiles': [],
                'overviewfiles': [],
                'contacts': [
                    {'id': 4,
                     'fullname': 'Saskia Restful Notificaties'}],
                'enrollmentmethods': ['manual'],
                'idnumber': '',
                'format': 'topics',
                'showgrades': 1,
                'newsitems': 5,
                'startdate': 1605740400,
                'enddate': 1637276400,
                'maxbytes': 0,
                'showreports': 0,
                'visible': 1,
                'groupmode': 0,
                'groupmodeforce': 0,
                'defaultgroupingid': 0,
                'enablecompletion': 1,
                'completionnotify': 0,
                'lang': '',
                'theme': '',
                'marker': 0,
                'legacyfiles': 0,
                'calendartype': '',
                'timecreated': 1605708824,
                'timemodified': 1605708824,
                'requested': 0,
                'cacherev': 1605801045,
                'filters': [{'filter': 'displayh5p', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'activitynames', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'mathjaxloader', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'emoticon', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'urltolink', 'localstate': 0, 'inheritedstate': 1},
                            {'filter': 'mediaplugin', 'localstate': 0, 'inheritedstate': 1}],
                'courseformatoptions': [{'name': 'hiddensections', 'value': 0},
                                        {'name': 'coursedisplay', 'value': 0}]}]
    }

test_learning_locker_viewed_course = \
    {
        "more": "",
        "statements": [
            {
                "actor": {
                    "name": "Admin User",
                    "account": {
                        "homePage": "http://127.0.0.1:80",
                        "name": "2"
                    },
                    "objectType": "Assistant"
                },
                "verb": {
                    "id": "http://id.tincanapi.com/verb/viewed",
                    "display": {
                        "en": "viewed"
                    }
                },
                "object": {
                    "id": "http://127.0.0.1:80/course/view.php?id=2",
                    "definition": {
                        "type": "http://id.tincanapi.com/activitytype/lms/course",
                        "name": {
                            "en": "BeginningCourse"
                        },
                        "extensions": {
                            "https://w3id.org/learning-analytics/learning-management-system/short-id": "BC",
                            "https://w3id.org/learning-analytics/learning-management-system/external-id": "7"
                        }
                    },
                    "objectType": "Activity"
                },
                "timestamp": "2019-10-16T11:26:19+01:00",
                "context": {
                    "platform": "Moodle",
                    "language": "en",
                    "extensions": {
                        "http://lrs.learninglocker.net/define/extensions/info": {
                            "http://moodle.org": "3.7.2 (Build: 20190909)",
                            "https://github.com/xAPI-vle/moodle-logstore_xapi": "v4.4.0",
                            "event_name": "\\core\\event\\course_viewed",
                            "event_function": "\\src\\transformer\\events\\core\\course_viewed"
                        }
                    },
                    "contextActivities": {
                        "grouping": [
                            {
                                "id": "http://127.0.0.1:80",
                                "definition": {
                                    "type": "http://id.tincanapi.com/activitytype/lms",
                                    "name": {
                                        "en": "\"New Site\""
                                    }
                                },
                                "objectType": "Activity"
                            }
                        ],
                        "category": [
                            {
                                "id": "http://moodle.org",
                                "definition": {
                                    "type": "http://id.tincanapi.com/activitytype/source",
                                    "name": {
                                        "en": "Moodle"
                                    }
                                },
                                "objectType": "Activity"
                            }
                        ]
                    }
                },
                "id": "c98c8522-3d43-4098-9b5d-812392458328",
                "stored": "2019-10-16T10:27:02.866Z",
                "authority": {
                    "objectType": "Assistant",
                    "name": "New Client",
                    "mbox": "mailto:hello@learninglocker.net"
                },
                "version": "1.0.0"
            }
        ]
    }
