<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * This file is responsible for collecting the required analytics data to be used in the dashboard modules
 *
 * @package local_boxdashboard
 * @author Joep
 */

require_once(__DIR__ . '/../../config.php');
require_once "config.php";
require_once "util.php";

header('Content-Type: application/json');

$courseId = optional_param('cid', -1, PARAM_INT);
$blockId = optional_param('bid', "", PARAM_TEXT);
$type = optional_param('type', "", PARAM_TEXT);

if (checkParameters($blockId, $courseId, $type)) {
    //Check if user has correct capabilities to access the dashboard of this course
    get_dashboard_authorization($courseId);

    //Get the data
    $data = acquireData($blockId, $courseId, $type);
    echo json_encode($data);
}

/**
 * Acquire the information that was requested given three (valid!) parameters
 *
 * @param string $blockId A valid blockid
 * @param int $courseId A valid courseid
 * @param string $type A valid analysis type
 * @return array The data requested
 */
function acquireData($blockId, $courseId, $type)
{
    require("modules/$blockId/module.php");
    require("modules/$blockId/config.php");
    require "config.php";

    $defaults = array(
        "blockname" => $blockId,
        "pluginPath" => $pluginPath,
        "initFunc" => $blockJS ? $blockId . "_" . $type . "_init" : "",
    );
    $method = $type == "block" ? "Block" : "Details";
    $data = ("module_" . $blockId . "_get" . $type . "Data")($courseId);
    $data = array_merge($defaults, $data);
    return $data;
}

/**
 * Check all the parameters
 *
 * @param string $blockId The blockid parameter to check
 * @param int $courseId The courseid parameter to check
 * @param string $type The type parameter to check
 * @return bool True if all valid, false if not
 */
function checkParameters($blockId, $courseId, $type)
{
    if (!checkTypeParam($type)) {
        return false;
    }
    if (!checkCourseParam($courseId)) {
        return false;
    }
    if (!checkBlockParam($blockId)) {
        return false;
    }

    return true;
}

/**
 * Check if the blockid paramater is valid and send the appropriate error message if not valid.
 *
 * @param string $blockId The blockid parameter to check
 * @return bool True if valid, false if not
 */
function checkBlockParam($blockId)
{
    require "config.php";
    if (empty($blockId)) {
        sendError("Parameter 'bid' is required");
        return false;
    }
    if (!in_array($blockId, $installedModules)) {
        sendError("Parameter 'bid' does not indicate a valid block");
        return false;
    }
    return true;
}

/**
 * Check if the courseid paramater is valid and send the appropriate error message if not valid.
 *
 * @param int $courseId The courseid parameter to check
 * @return bool True if valid, false if not
 */
function checkCourseParam($courseId)
{
    if ($courseId < 0) {
        sendError("Invalid 'cid' parameter");
        return false;
    }
    global $DB;
    if ($DB->count_records('course', ['id' => $courseId]) != 1) {
        sendError("A course with id=$courseId does not exist.");
        return false;
    }
    return true;
}

/**
 * Check if the type paramater is valid and send the appropriate error message if not valid.
 *
 * @param string $type The type parameter to check
 * @return bool True if valid, false if not
 */
function checkTypeParam($type)
{
    if (empty($type)) {
        sendError("Parameter 'type' is required");
        return false;
    }
    if ($type != "details" && $type != "block") {
        sendError("Parameter 'type' must be either 'details' or 'block'");
        return false;
    }
    return true;
}

/**
 * Echo an error to the page in order to 'send' an error
 *
 * @param string $message The error message to send
 * @return void
 */
function sendError($message)
{
    echo json_encode(array(
        "error" => $message
    ));
}
