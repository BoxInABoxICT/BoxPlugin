# Mofa setup

Mofa is a python webserver using the Django framework. It is a tool to analyze data from with the LRS and handle data sending to Moodle.

To setup the mofa client follow instructions below. There is a slightly different setup for local development environment and production.

## Environment settings
Open the file `mofa/.env` in an editor. Find the Moodle and LRS endpoint URLs, and adjust the variables accordingly. These URLs may include port numbers. When the LRS app is hosted on the same server using docker, you may also want to use the internal docker ipv4 address, e.g. `LL_URL=http://172.20.0.16:80`. This is optional but can prevent errors.

# TimeZone
TIME_ZONE = Europe/Amsterdam

## Docker
For launching this application docker and docker-compose are needed. Follow install instructions from [the docker site](https://docker.com). Made for and tested on docker-compose version 3.8.

### Dockerfile
This file creates an image from the source code within this directory. It uses Python 3 and installs all neccesary plugins mentioned in the requirements.txt file. This will automatically rebuild when calling docker-compose.

### Local development
1. Go into a terminal and navigate to the directory in which the `up-local.yml` file is located. Run the docker-compose file for local development. 
* The `-f` flag defines which file to use. 
* The `-d` flag dettaches the container
```bash
docker-compose -f up-local.yml up -d
```
2. Give it some time to run, a first-time run will take some time. Check if no errors have occured by typing 
```bash
docker-compose -f up-local.yml logs
```
3. Once everything is set up, create a new user. Use the command below and follow the instructions on screen.
```bash
docker exec -it build_mofa_web_local python manage.py createsuperuser
```

4. When you have created a user, the next step is to create an authentication token for that user. Boxconnect requires an authentication token in order to connect with Mofa's analytics app. If you created the user account of step 6 with the name admin, creating the authentication token would look like this. For more info how to use it, check the [authentication guide](analytics/docs/authentication.md).
```bash
python manage.py drf_create_token admin
```

5. The Mofa server is now running at http://localhost:8003. Log in using the credetials created in the previous step.


### Production environment
1. Make sure to create a network called *routing_proxy*.
```bash
docker network create routing_proxy
```
or run the setup script (use sudo if needed)
```bash
chmod +x setup.sh && ./setup.sh
```
2. (Optional) Setup a Traefik instance via Docker and edit the labels in the `up-prod.yml` file to match your setup. If you are not using a routing proxy, remove or comment the lines.
3. Go into a terminal and navigate to the directory in which the `up-local.yml` file is located.
4.  Run the docker-compose file for local development. 
* The `-f` flag defines which file to use. 
* The `-d` flag dettaches the container
```bash
docker-compose -f up-prod.yml up -d
```
5. Give it some time to run, a first-time run will take some time. Check if no errors have occured by typing 
```bash
docker-compose -f up-prod.yml logs
```
6. Once everything is set up, create a new user. Use the command below and follow the instructions on screen.
```bash
docker exec -it build_mofa_web python manage.py createsuperuser
```

7. When you have created a user, the next step is to create an authentication token for that user. Boxconnect requires an authentication token in order to connect with Mofa's analytics app. If you created the user account of step 6 with the name admin, creating the authentication token would look like this. For more info how to use it, check the [authentication guide](analytics/docs/authentication.md).
```bash
python manage.py drf_create_token admin
```

8. The Mofa server is now running at http://<mofa>.<your-domain>. Log in using the credetials created in the previous step.

## Running tests
Running Python unit tests (for local development)
```bash
docker exec -it build_mofa_web_local python manage.py test 
```

## Making changes
After making changes to the python code, simple re-run the `docker-compose -f <version> up -d` command. This will rebuild and make database migrations for your. When using more libraries, do not forget to include them in requirements.txt.

# Credits
Initial Mofa code provided by Sting-IT (c) Utrecht University 2019. Extended and containerized by Box-in-a-Box ICT 2020 through the [analytics application](analytics/docs/README.md).


