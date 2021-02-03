<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * In this file, some basic settings for the plugin can be configured.
 * This is the only place where the plugin name and path are mentioned. To change the name, you only have to change these settings.
 *
 * @package local_boxdashboard
 * @author Joep
 */

$pluginPath = "/local/boxdashboard";
$internalName = "local_boxdashboard";

$usersettingsPath = "$pluginPath/usersettings.php";

//Stylesheets to include on the course statistics page. (includes from the stylesheets folder in the plugin root)
$stylesheets = array(
    "Chart.css"
);

//Scripts to include on the course statistics page. (includes from the scripts folder in the plugin root)
$scripts = array(
    "Chart.js",
    "Chartjs_boxplot.js",
    "Lodash.js",
    "Util.js",
    "ChartManager.js",
    "AsyncDataLoader.min.js",
    "AsyncSettingHandler.min.js",
    "template7.min.js"
);

//Modules in the boxdashboard/modules folder that should be used on the dashboard
$installedModules = array(
    "viewcount",
    "studenttime",
    "participation",
    "dialoguetrainer",
    "dtpageviews",
);
