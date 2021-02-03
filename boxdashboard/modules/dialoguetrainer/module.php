<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * This file is responsible for retrieving data for the main block on the dashboard for the dialoguetrainer analytics module
 *
 * @package local_boxdashboard.modules.dialoguetrainer
 * @author Joep
 */

require_once __DIR__ . "/../../config.php";
require_once __DIR__ . "/../../util.php";


/**
 * Function called by the dataloader to get the data for the analytics block on the dashboard
 *
 * @param int $courseID The id of the course to get the analytics data of
 * @return array An associative array with all the data
 */
function module_dialoguetrainer_getBlockData($courseid)
{
    return [
        "scenarios" => array_map(function ($id) {

            $boxdashboard =  django_request("analytics/dt/bestattempts/$id");
            $boxdashboard['id'] = $id;
            return $boxdashboard;
        }, module_dialoguetrainer_getCourseScenarios($courseid))
    ];
}

/**
 * Function called by the dataloader to get the data for the details panel on the dashboard
 *
 * @param int $courseID The id of the course to get the analytics data of
 * @return array An associative array with all the data
 */
function module_dialoguetrainer_getDetailsData($courseid)
{
    $scenarios = module_dialoguetrainer_getCourseScenarios($courseid);
    $scenarioData = [];
    foreach ($scenarios as $scenario) {
        $scenarioData[$scenario] = module_dialoguetrainer_getDialogueTrainerAnalytics($scenario);
    }
    return [
        "scenarios" => $scenarioData
    ];
}

/**
 * Function called to get the data for the dashboard for one specific dt scenario
 *
 * @param int $id The id of the scenario to get the analytics data of
 * @return array An associative array with all the data
 */
function module_dialoguetrainer_getDialogueTrainerAnalytics($id)
{
    $betweenAttempts = django_request("analytics/dt/betweenstudentattempts/$id");
    $betweenStudents = django_request("analytics/dt/betweenstudents/$id");
    return [
        "betweenStudents" => $betweenStudents,
        "betweenAttempts" => $betweenAttempts
    ];
}

/**
 * TODO make it not hardcoded
 * A function that returns all the dialoguetrainer scenarios that belong to a specific course
 *
 * @param int $courseID The id of the course to get the scenarios of
 * @return array An array with all the scenario ids
 */
function module_dialoguetrainer_getCourseScenarios($courseid)
{
    return [
        1300,
        1315,
        1343,
        1344,
        1375,
        1726,
        1797
    ];
}
