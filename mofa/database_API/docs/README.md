# Dashboard
The `boxdashboard` dashboard will support the remote configuration of two types of MOFA settings:
- Course settings
- Assistant configuration/settings

# Database API refrence
The database API offers an interface for remote configuration of a select amount of MOFA features. This API has been made to work together with our own dashboard `boxdashboard`, a moodle plugin for which more information can be found [here](../../../boxdashboard/README.md), however any interface able to make HTTP requests will be able to communicate with the API.

## Course settings
MOFA offers the possibility for teachers to send automated messages to students participating in a course when a student hasn't submitted an assignment an amount of time before an assignment deadline and/or when a student hasn't visited the course pages in a certain amount of time. Django's [`views.py`](../views.py) file is the entrypoint for processing any requests from the dashboard. It operates according to two modes dictated by the type of HTTP request it recieves:

- `GET`: Fetches the current course settings and returns them according to the course settings format.
- `POST`: Complimented by new values for the course settings in the request body. This request will update the course settings in MOFA and afterwards return the updated course setting values back to the dashboard in the same format as the `GET` request.

For the exact formatting required and returned by these requests see the [formatting document](./formFormat.md)

## Assistant settings
Course assistants are virtual assistants that can automatically execute (routine) tasks. One such assistant implemented is the NewActivityCreated assistant which, when linked to a course, will send notifications to all participating students whenever a teacher adds new activities to the course. The remote configuration of these assistants work in a similair manner as the course settings.  Django's [`views.py`](../views.py) again contains the entrypoint for processing dashboard requests, using a different URL endpoint compared to Course settings. Assistant settings also functions in two modes dictated by the type of http request recieved:

- `GET`: Fetches the current assistants and their configuration linked to the course and returns them according to the assistant settings format.
- `POST`: Complimented by new values for the assistant(s) settings in the request body. This request will update the assistant settings in MOFA and afterwards return the updated course setting values back to the dashboard in the same format as the `GET` request.

For the exact formatting required and returned by these requests see the [formatting document](./formFormat.md)

# Further Development
To ease implementing new assistants/features the [development document](./development.md) points out the functions required to modify to facilitate a larger variety of settings and assistants.