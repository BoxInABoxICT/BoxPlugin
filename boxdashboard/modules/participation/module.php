<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * This file is responsible for retrieving data for the main block and details panel on the dashboard for the participation analytics module
 *
 * @package local_boxdashboard.modules.participation
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
function module_participation_getBlockData($courseid)
{
    return array(
        "pageviews" => module_participation_getPageParticipation($courseid)
    );
}

/**
 * Function called by the dataloader to get the data for the details panel on the dashboard
 *
 * @param int $courseID The id of the course to get the analytics data of
 * @return array An associative array with all the data
 */
function module_participation_getDetailsData($courseid)
{
    $result = array(
        "quizCompletion" => module_participation_getCompletion($courseid, "quiz", "quiz"),
        "assignmentCompletion" => module_participation_getCompletion($courseid, "assignment", "assign"),
        "pageviews" => module_participation_getPageParticipation($courseid)
    );
    return $result;
}

/**
 * Get the page participation from django
 *
 * @param int $courseid The id of the course to get the participation analysis of
 * @return array Associative array containing all the data
 */
function module_participation_getPageParticipation($courseid)
{
    global $DB;
    $result = django_request("analytics/participation/page/$courseid");

    $pageids = array_map('getIdFromUrl', array_keys($result));
    $data = array_combine($pageids, array_values($result));

    $studentcount = intval(get_courses_enrolment_count()[$courseid]->enrolments);

    $modules = array_keys($DB->get_records("course_modules", array("course" => $courseid)));

    $result = array();

    foreach ($modules as $id) {
        $moduleData = get_module_info($id);
        $moduleData["percentage"] = array_key_exists($id, $data) ? $data[$id] / $studentcount : 0;
        $result[$id] = $moduleData;
    }

    return array_values($result);
}

/**
 * Get the quiz participation from django
 *
 * @param int $courseid The id of the course to get the participation analysis of
 * @param string $participation The name of the analysis in the /participation/$participation/$courseid path
 * @param string $modName The name of the module in moodle internal
 * @return array Associative array containing all the data
 */
function module_participation_getCompletion($courseid, $participation, $modName)
{
    global $DB;
    $result = django_request("analytics/participation/$participation/$courseid");

    $moduleIds = array_map('getIdFromURL', array_keys($result));
    $data = array_combine($moduleIds, array_values($result));

    $studentcount = intval(get_courses_enrolment_count()[$courseid]->enrolments);
    $assignmentID = $DB->get_record("modules", array("name" => $modName))->id;
    $allAssignments = array_keys($DB->get_records("course_modules", array("course" => $courseid, "module" => $assignmentID)));

    $result = array();

    foreach ($allAssignments as $id) {
        $allInfo = get_module_info($id);
        $allInfo["percentage"] = array_key_exists($id, $data) ? $data[$id] / $studentcount : 0;
        $result[$id] = $allInfo;
    }

    return array_values($result);
}
