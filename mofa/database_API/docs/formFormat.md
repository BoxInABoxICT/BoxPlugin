# Course settings formatting

## Returned settings format

The JSON structure the database API uses to return the course settings to the dashboard is as follows:
```Json
{
    "status": "<the exit status of the pipeline that returned this message (succes/error)>",
    "statusType": "<the type of request being answered (fetch/update)>",
    "message": "<human readable message indicating the status of the request",
    "objects": {
        "deadline": {
            "enabled": false,
            "title": "Deadline notifications",
            "description": "Notify a student when a deadline approaches in set hours.",
            "currentValue": 24,
            "valueType": "hours"
        },
        "inactivity": {
            "enabled": false,
            "title": "Inactivity notifications",
            "description": "Notify a student when he/she has not been active for set amount of time.",
            "currentValue": 7,
            "valueType": "days"
        }
    }
}
```
The `objects` key contains representations of all configurable course settings. In the current version only two are present, but can be easily extended to feature more settings.

Each of the setting objects must have the following structure to be properly rendered in the dashboard:
```Json
{
    "<key/name of the setting>": {
        "enabled": <Boolean value for toggling the setting>,
        "title": "<human readable title>",
        "description": "<human readable description>",
        "currentValue": <Integer value>,
        "valueType": "<human readable metric used for currentValue (weeks/days/hours/etc. depends on setting in question>"
    }
}
```

## Forwarded settings format

The course settings that require an update in MOFA are forwarded in a `POST` request body and need to adhere to the following JSON format:
```Json
{
    "request_type": "update",
    "data":
        [
          {"name":"<settingkey>-<settingattribute>","value":"<corresponding value>"},
          {...}
        ]
}
```
`settingkey` identifies which course setting gets updated.
`settingattribute` identifies the field of the setting that has to be updated (`enabled`,`value`)
and the `corresponding value` then has to be set to the desired value for the setting.

Here follows an example of this format where _all_ the remotely configurable course settings get updated:
```Json
{
    "request_type": "update",
    "data":
        [
          {"name":"deadline-enabled","value":"true"},
          {"name":"deadline-value","value":"48"},
          {"name":"inactivity-value","value":"8"},
          {"name":"inactivity-enabled","value":"false"}
        ]
}
```
*note: not all course setting-attributes have to be present in the list, the following request body is also valid:*
```Json
{
    "request_type": "update",
    "data":
        [
          {"name":"deadline-enabled","value":"true"}
        ]
}
```
And will only override the `enabled` state of the `deadline` course setting.

# Assistant settings formatting

## Returned settings format

The JSON structure the database API uses to return the assistant settings to the dashboard is largely similair to the course settings:
```Json
{
    "status": "<the exit status of the pipeline that returned this message (succes/error)>",
    "statusType": "<the type of request being answered (fetch/update)>",
    "message": "<human readable message indicating the status of the request",
    "objects": {
        <objects representing the state of each assistant for the course>
    }
}
```

The exact formatting for the assistant objects can be quite flexible assuming that parsing of these objects has been properly implemented. For the current Assistants present we adhere to the following format:

### NewActivity Assistant

The NewActivity Assistant has a very basic functionality in its current implementation and therefore it only implements the bare minumum of required fields.
```Json
{
    "<key/name of the assistant>": {
        "name": "<human readable assistant name>",
        "description": "<(optional) human readable description of the assistant>",
        "dbAction": "<indicating what happened to the assistant (added/updated/removed)>"
    }
}
```

### QuizCompletedFeedback

*`Important note: The database API does not contain any functionality for configuring this assistant type in the database due to the Quiz feedback assistant not actually working in the mofa implementation. The API however still has parsing functionality for this assistant so that it may serve as an example for future assistant implementations (or for when someone fixes the quiz feedback assistant).`*

The QuizCompletedFeedback Assistant has a single user configurable field (the score threshold) and this gets reflected in the object by simply adding a single extra field to the object.
```Json
{
    "<key/name of the assistant>": {
        "<quizId>": {
            "title": "<human readable assistant name>",
            "description": "<(optional) human readable description of the assistant>",
            "dbAction": "<indicating what happened to the assistant (added/updated/removed)>",
            "score_threshold": <integer>
        }
    }
}
```

## Forwarded settings format

The assistants that require an update in MOFA are forwarded in a `POST` request body similair to the course settings and need to adhere to the following JSON format:
```Json
{
    "request_type": "update",
    "data":
        [
          {"name":"<assistantKey>-<assistantAttribute>","value":"<corresponding value>"},
          {...}
        ]
}
```
`assistantKey` identifies which course setting gets updated (`new_activity`,`quiz_feedback`).
`assistantAttribute` identifies the field of the setting that has to be updated, available attributes differ per assistant, `corresponding value` then has to be set to the desired value for the refrenced attribute.

### New Activity Assistant attributes

Attributes and their values able to be set for the new activity course assistant:

`dbAction` (`add`, `remove`, `fetch`): What action mofa should exectute on the forwarded assistant.
*note: The new Activity Assistant has no further attributes as its only behavior in the current implementation is to (immediately) notify students about newly added activities to the course.*

### Quiz Feedback Assistant attributes

Attributes and their values able to be set for the quiz completed course assistant:

`dbAction` (`add`, `update`, `remove`, `fetch`): What action mofa should exectute on the forwarded assistant.
`quizId` (`<integer>`): Moodle Id of the quiz to provide feedback for.
`provide_feedback` (`<boolean> default:true`): Toggle the active state of the assistant.
`score_treshold` (`<integer> default:55`): Treshold on the quiz score for which to provide feedback.

*note: due to the nature of the quizAssistant certain actions will require certain fields to be present to succeed*
- The dbActions `add`, `update`, `remove` will require a `quizId` to be provided to specify which quizAssistant to perform the action on.
- The dbAction `update` will additionally require at least one of the following attributes: `provide_feedback` or `score_treshold` for the update action to make any sense/have any effect.