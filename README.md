# Box-in-a-Box ICT Repo
[![pipeline status](https://git.science.uu.nl/d.o.owolabi/moodlefeedback/badges/Development/pipeline.svg)](https://git.science.uu.nl/d.o.owolabi/moodlefeedback/-/commits/Development)
[![code coverage](https://git.science.uu.nl/d.o.owolabi/moodlefeedback/badges/Development/coverage.svg)](https://git.science.uu.nl/d.o.owolabi/moodlefeedback/-/commits/Development)

## Copyright
This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software and Game project course.

©Copyright Utrecht University Department of Information and Computing Sciences.

## In this repo
This repo exists out of multiple software tools that can be run via either docker or by manually building it. This repo contains all necessary software to reprocude the whole project, including the open-source software required to start up store data, and install plugins on. 

This repo contains the following software. Each directory contains their own README file explaining the use and setup.

- /
    - **boxconnect** The custom plugin for Moodle / LLL which makes it possible to connect to mofa for analysis to add extended LLL functionality.
    - **boxdashboard** A plugin that creates an analysis dashboard for moodle.
    - **boxlogstore** A modified version of the logstore_xapi plugin, used to forward statements to the LRS.
    - **DataPseudonymizer** A piece of software to extract data from an existing LLL environment. This tool makes sure the data is made anonymous to be used as test-data for other software in this project.
    - **learninglocker** An open source LRS. Run this to store xApi statements at a certain endpoint.
    - **LLLconverter** An utility tool for manually converting a set of LLL data to xAPI statements.
    - **mofa** An extended and containerized version of Sting-IT 2019's mofa client. This is a Django webapp and uses to data from the LRS to enrich the LLL functionlity. This means sending notifications and generating analysis.
    - **moodle_plugins** A directory containing zipped, unmodified, open-source plugins that need to be installed.
    - **moodle_standalone** A directory containing the moodle image used for this project.
    - **test_data** An utility tool used for manually converting DT data to xAPI statements.
    - **.gitlab-ci.yml** A gitlab pipeline created for automated unit testing.


## Run a local stack

This repo contains open source versions of [Moodle](https://docs.moodle.org/310/en/Main_page) and LRS (version: [Learning Locker](https://docs.learninglocker.net/welcome/)). We assume these are already installed. If not, guides can be found on the internet.

### Requirements
- `Docker` and `docker-compose`. All OS are supported.
- A Mofa client (this is the code that can be found in the /mofa directory in this repo, setup will follow in the instructions below)
- An instance of `Moodle` (hosted anywhere) and a user with full permissions. *
    - (Plugin) **logstore_xapi**, An open-source plugin that pushes moodle actions to an endpoint in xApi format. Latest version [here](https://moodle.org/plugins/logstore_xapi).
    - (Plugin) **Restful**, An open-source plugin that enables the restful protocol at an endpoint in moodle. Latest version [here](https://moodle.org/plugins/webservice_restful)
    - (Plugin) **Boxconnect**, A Box-in-a-Box plugin to connect the Moodle to the analysis component of your Mofa instance. Latest version [in this repo](boxconnect/).
    - (Plugin) **boxdashboard**, A Box-in-a-Box plugin to show statistics in a dashboard for teachers. Latest version [in this repo](boxdashboard/).
- An instance of `Learning Locker` (LRS) *

_*This should be reachable for other services in this stack. Make sure this is hosted on a server and you have an endpoint (e.g. https://server.com/data/xApi) or use `http://localhost` when using locally for development._

## Installation
1. Run `mofa` and install the `Restful` plugin on the `Moodle` instance. Follow the steps in [this guide](https://mofa.readthedocs.io/en/latest/index.html). 

    NOTE: this guide also helps you install Docker and a local moodle and configure the LRS. You may be able to skip some steps depending on your current setup.

    NOTE: In the newer version of mofa, `docker-compose` is used to create the stack. Instead of
    ```bash
    python manage.py runserver 0.0.0.0:8003
    ```
    simply run 
    ```bash
    docker-compose up --build -d
    ```
    You don't need to install python and the dependencies locally. Docker will do this for you. 
    
    If you decide to use your local python environment, make sure to also install a postgres service and configure this in `mofa/mofa/settings.py`.
2. In your running `mofa` client, log in and create a token in the admin panel.
3. Go to the running `Moodle` client, log in and install the `logstore_axpi` plugin. 

    3.1 Enable the plugin in `Site Administration > Plugins > Logging > Manage` and use the eye icons to toggle `Logstore xApi` to *enable*.

    3.2 Press `settings` on this page.

    3.3 Enter the the `xApi Endpoint`, `Key` and `Secret` from the `LRS client` created in step 1. These need to be filled into the fields `Your LRS endpoint for the xAPI`, `Your LRS basic auth key/username for the xAPI`, `Your LRS basic auth secret/password for the xAPI` in `Moodle`.

    3.4 (Development only) Disable `Send statements by scheduled task`

    3.5 Enable `Send course and activity ID number` and `Identify users by id`

    3.6 Press save.

    3.7 Visiting a course or page should now result in a statement in your `LRS`
4. Install the `boxconnect` plugin in `Moodle`. The easiest way to install this is zipping the `boxconnect` directory and instaling it via the `Moodle` GUI. For more information refer to the documentation in the plugin folder.
5. Install the `boxdashboard` plugin. The easiest way to install this is zipping the `boxdashboard` directory and instaling it via the `Moodle` GUI. This depends on the boxconnect plugin.
6. The dashboard is now visiable in the left menu. Make sure to set yourself as a teacher of course to be able to see it's dashboard.




 