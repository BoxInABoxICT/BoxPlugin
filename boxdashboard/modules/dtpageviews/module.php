<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * This file is responsible for retrieving data for the main block on the dashboard for the dtpageviews analytics module
 *
 * @package local_boxdashboard.modules.dtpageviews
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
function module_dtpageviews_getBlockData($courseid)
{

    return [
        "scenarios" => array_map(function ($id) {

            $boxdashboard =  django_request("analytics/dt/pageviews/$id/e17294c6");
            $boxdashboard['id'] = $id;
            return $boxdashboard;
        }, module_dtpageviews_getCourseScenarios($courseid))
    ];
}

/**
 * TODO make it not hardcoded
 * A function that returns all the dialoguetrainer scenarios that belong to a specific course
 *
 * @param int $courseID The id of the course to get the scenarios of
 * @return array An array with all the scenario ids
 */
function module_dtpageviews_getCourseScenarios($courseid)
{

    return [
        1148,
        1300,
        1315,
        1343,
        1344
    ];
}
