<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

require_once(__DIR__ . '/../../config.php');
require_once "config.php";
require_once "util.php";

$boxconnectdir = $_SERVER['DOCUMENT_ROOT'] . '/local/boxconnect/src/';
require_once $boxconnectdir . 'HttpRequest.php';

header('Content-Type: application/json');

$courseId = optional_param('cid', -1, PARAM_INT);
if (!checkCourseParam($courseId)) {
    return;
}

//Check if user has correct capabilities to access the dashboard of this course
get_dashboard_authorization($courseId);

$mockresult = array(
    "status" => "success",
    "status_type" => "update",
    "message" => "Settings updated successfully",
    "objects" => array(
            "deadline" => array(
                "enabled" => true,
                "title" => "Deadline notifications",
                "desc" => "Notify a student when a deadline approaches in set hours.",
                "currentValue" => 8,
                "valueType" => "hours"
            ),
            "inactivity" => array(
                "enabled" => false,
                "title" => "Inactivity notifications",
                "desc" => "Notify a student when he/she has not been active for set of time.",
                "currentValue" => 2,
                "valueType" => "days"
            )
        )
);



switch ($_SERVER["REQUEST_METHOD"]) {
    case "POST":
        $requestBody = file_get_contents('php://input', true);
        $result = json_encode(django_request("db/courseSettings/$courseId", $requestBody));
        echo $result;
        break;

    case "GET":
        $result = json_encode(django_request("db/courseSettings/$courseId"));
        echo $result;
        break;

    default:
        sendError("Unsuppored request method");
        return;
}

function checkCourseParam($courseId)
{
    if ($courseId < 0) {
        sendError("Invalid 'cid' parameter");
        return false;
    }
    global $DB;
    if ($DB-> count_records('course', ['id' => $courseId]) != 1) {
        sendError("A course with id=$courseId does not exist.");
        return false;
    }

    return true;
}

function sendError($message)
{
    echo json_encode(array(
        "error" => $message
    ));
}
