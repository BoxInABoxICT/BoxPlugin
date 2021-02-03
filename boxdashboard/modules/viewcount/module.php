<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * This file is responsible for retrieving data for the main block and details panel on the dashboard for the viewcount analytics module
 *
 * @package local_boxdashboard.modules.viewcount
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
function module_viewcount_getBlockData($courseID)
{
    $dataArray = array();
    $dataArray = array_merge($dataArray, module_viewcount_getGraphData($courseID));
    return $dataArray;
}

/**
 * Function called by the dataloader to get the data for the details panel on the dashboard
 *
 * @param int $courseID The id of the course to get the analytics data of
 * @return array An associative array with all the data
 */
function module_viewcount_getDetailsData($courseID)
{
    $dataArray = array();
    $dataArray = array_merge($dataArray, module_viewcount_getSimpleCount($courseID));
    $dataArray = array_merge($dataArray, module_viewcount_getGraphData($courseID));
    return $dataArray;
}

/**
 * Query django to get the total view count analytics
 *
 * @param int $courseID The id of the course to get the count of
 * @return array An array containing a single key: 'count', with as value the total visit count.
 */
function module_viewcount_getSimpleCount($courseID)
{
    $result = django_request("analytics/viewed/count/$courseID");
    return array(
        'count' => $result["count"]
    );
}

/**
 * Query django to get the view count of each page in the course per day
 *
 * @param int $courseID The id of the course to get de data for
 * @return array An array with one key containing an array of associative arrays each containing information about a single page in the course
 */
function module_viewcount_getGraphData($courseID)
{
    $result = django_request("analytics/viewed/history/$courseID");

    $mapping = function ($key, $data) {
        $id = getIdFromURL($key);
        $newData = get_module_info($id);
        $newData["points"] = $data;
        return $newData;
    };

    $result = array_map($mapping, array_keys($result), array_values($result));
    $result = array_values(array_filter($result));

    return array(
        'graphs' => $result,
    );
}
