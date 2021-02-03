# boxdashboard plugin

## Copyright
This program has been developed by students from the bachelor Computer Science at Utrecht University within the Software and Game project course.

©Copyright Utrecht University Department of Information and Computing Sciences.

## Purpose

This plugin adds a dashboard to moodle that can be used together with the MOFA component to provide learning statistics to teachers.

## Requires
* The __boxplugin__ for data retrieval.
* The __MOFA__ component for data analysis.
* A working __moodle__ installation
* Will only work on courses of type __topics__

## Instalation

Simply go to the plugin install page of moodle and drop the `boxdashboard.zip` file into the box and click install.


## Structure
* __*lang / en*__
    * __local_boxdashboard.php__ This file contains all the language strings used troughout the plugin. When rendering, a prefix of `lang_` is added.
* __*modules*__ This folder contains all the statistics `modules`. Each of these modules shows a certain statistic on the `dashboard`. The modules have to follow a very strict structure.
    * __*{{examplemod}}*__ This is the folder of an example module. 
        * __config.php__ __[REQUIRED]__ Should contain the following variables: 
            * `fullname` :string
            * `visualisationtype` :string,
            * `blockJS`:bool
            * `blockCSS`:bool
            * `hasDetails`:bool
            * `detailJS`:bool
            * `detailCSS`:bool
        * __module.php__ __[REQUIRED]__ 
            *  Should contain the function `module_{{examplemod}}_getBlockData(courseid:int)` that returns an associative array with all the data that is required for the dashboard module.
            * [IF `hasDetails` is set to `true`] Should contain the function `module_{{examplemod}}_getDetailsData(courseid:int)` that returns an associative array with all the data that is required for the details module. 
        * __block.js__ [IF `blockJS` is set to `true`]
            *  Should contain a function `{{examplemod}}_block_init(data:json)` That is called when the data from the `module.php` function is available.
        * __block.css__ [IF `blockCSS` is set to `true`]
            * Contains styling rules for the module on the dashboard. All rules should have a `{{examplemod}}_block_` prefix.
        * __details.js__ [IF `detailsJS` and `hasDetails` are set to `true`]
            *  Should contain a function `{{examplemod}}_details_init(data:json)` That is called when the data from the `module.php` function is available.
        * __details.css__ [IF `detailsCSS` and `hasDetails` are set to `true`]
            * Contains styling rules for the details panel of the module on the dashboard. All rules should have a `{{examplemod}}_details_` prefix.
    * __...__ Each additional module would also be in such a folder.
* __*scripts*__ Contains all the global javascript files for the dashboard
    * __AsyncDataLoader.js__ Responsible for async data loading on the dashboard. This makes sure the data for modules is only loaded when you click on the module.
    * __Chart.js__ The library used for graph visualisations
    * __ChartManager.js__ A wrapper for the `Chart.js` library to make graphs easier to use.
    * __Util.js__ Some utility functions used throughout the dashboard.
* __*stylesheets*__ Contains all the global stylesheets for the dashboard and the course list.
    * __Chart.css__ The stylesheet that comes with the `Chart.js` library.
    * __courselist.css__ The stylesheet meant for the `courselist.php` page.
    * __dashboard.css__ The stylesheet meant for the `dashboard.php` page
* __*templates*__ The rendering templates used in te plugin. A rendering template allows to create a html page with placeholders. Those placeholders will later be replaced by strings passed to the renderer.
    * __*modules*__ A folder containing all the templates for different modules.
        * __*{{examplemod}}*__ A folder containing the templates for the example module
            * __block.mustache__ __[REQUIRED]__ The template to render on the main dashboard page.
            * __details.mustache__ [IF `hasDetails` is set to `true`] The template to render inside the details panel.
        * __...__ A folder for each additional module that is installed.
    * __dashboard.mustache__ The template used to render the dashboard.
    * __courselist.mustache__ The template used to render the course list.
* __config.php__ In this file multiple settings for the plugin are configured.
    * `stylesheets`: an array of all the stylesheets in the `/stylesheets` folder to include on the page.
    * `scripts`: an array of al the scripts in the `/scripts` folder to include on the page.
    * `installedModules`: an array of names of all the modules in the `/modules` folder that should be used in the plugin.
* __courselist.php__ The file responsible for rendering the `courselist.mustache` template with the correct information.
* __dashboard.php__ The file responsible for rendering the `dashboard.mustache` template with the correct information.
* __dataloader.php__ The file that collects all the data when a request is made by the `AsyncDataLoader.js`.
* __lib.php__ Only has a single function, which makes sure the `Course statistics` element is visible in the moodle menu.
* __util.php__  Contains some utility functions
* __version.php__ A moodle required file containing version information of the plugin.