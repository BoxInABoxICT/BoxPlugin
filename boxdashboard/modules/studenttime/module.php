<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * This file is responsible for retrieving data for the main block on the dashboard for the studenttime analytics module
 *
 * @package local_boxdashboard.modules.studenttime
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
function module_studenttime_getBlockData($courseid)
{
    return module_studenttime_getGraphData($courseid);
}

/**
 * Query django to get the engagement time of each page in the course per day
 *
 * @param int $courseID The id of the course to get de data for
 * @return array An array with one key containing an array of associative arrays each containing information about a single page in the course
 */
function module_studenttime_getGraphData($courseid)
{
    $result = django_request("analytics/engagementTime/$courseid");
    $mapping = function ($key, $data) {
        $id = getIdFromURL($key);
        $newData = get_module_info($id);
        $newData["points"] = $data;
        return $newData;
    };
    $result = array_map($mapping, array_keys($result), array_values($result));
    $result = array_values(array_filter($result));
    return array(
        "graphs" => $result
    );
}
