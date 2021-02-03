<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * This file is responsible for generating and displaying the main page of the plugin. Here you can select the course to view the statistics of.
 *
 * @package local_boxdashboard
 * @author Joep
 */

//Include all the required files and variables
require_once(__DIR__ . '/../../config.php');
global $CFG;
global $DB;
require_once "config.php";
require_once "util.php";

//Check if user has correct capabilities to access the boxdashboard plugin
get_courselist_authorization();


//----------------------------
//        Setup page
//----------------------------
$PAGE->set_url(new moodle_url("$pluginPath/courselist.php"));
$PAGE->set_context(\context_system::instance());
$PAGE->requires->css("$pluginPath/stylesheets/courselist.css");
$PAGE->set_title(get_string('displayname', $internalName));
$PAGE->navigation->add(get_string('displayname', $internalName), new moodle_url("$pluginPath/courselist.php"))->make_active();     //Setup the navigation


//----------------------------
//      Setup page data
//----------------------------

//Get the course data from the moodle database
$courses = get_courses_enrolment_count();

//Filter the courses out for which the user does not have the right capabilities
$courses = array_filter($courses, function ($elem) {
    return has_capability('local/boxdashboard:boxdashboard', context_course::instance($elem->courseid));
});

//Create a context array to use in the template
$maincontext = [
    'courses' => array_map(function ($elem) {
        $elem->modules = get_emodule_count($elem->courseid);
        $elem->topics = count(get_course_topics($elem->courseid));
        $elem->hasStarted = getdate()[0] > $elem->startdate;
        $elem->hasEnded = getdate()[0] > $elem->enddate && $elem->enddate != 0;
        return $elem;
    }, array_values($courses)),
    'courseURL' => "$pluginPath/dashboard.php",
    'usersettingsPath' => $usersettingsPath
];

$lang = get_entire_language();
$maincontext = array_merge($maincontext, $lang);


//----------------------------
//      Render the page
//----------------------------
echo $OUTPUT->header(get_string('displayname', $internalName));
echo $OUTPUT->render_from_template("$internalName/courselist", $maincontext);
echo $OUTPUT->footer();

//=========================================================================================================
