# Copyright
This program has been developed by students from the bachelor Computer Science at Utrecht University within the
Software and Game project course

©Copyright Utrecht University Department of Information and Computing Sciences.


# Engagement time analytics

A module in the analytics Django app allowing insight into time spent by users on course pages.

## analyseTimeOnPage.py
The entrypoint for the analytics pipeline `analyseModuleVisitIime` gets called through the Django views interface.

### analyseModuleVisitTime()
- `analyseModuleVisitIime` accepts a single argument `courseID` which should be the moodle ID for the main course Page
- `analyseModuleVisitIime` returns a json formatted string containing data created by the analysis
- The json structure is as follows: `{xAPI-course-page-ids-as-key: [(tuples containing analysis data for the page)]}`
```json
{
    "<course page id>": [
        {
            "date":"<date in standard datetime format as string>",
            "time":"<total time in seconds>",
            "count":"<total visits for this page as string>"
        },
        {
            "date":"<another date>",
            "time":"<total time>",
            "count":"<total visits for this page>"
        }
    ],
    "<another course page id>": [
        {
            "date":"<date>",
            "time":"<total time>",
            "count":"<total visits for this page>"
        }
    ]
}
```