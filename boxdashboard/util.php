<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * This file contains some utility functions used throughout the boxdashboard plugin.
 *
 * @package local_boxdashboard
 * @author Joep
 */

$boxconnectdir = __DIR__ . '/../boxconnect/src/';
require_once $boxconnectdir . 'DjangoRequester.php';

/**
 * Get the courses and the amount of enrolments from the moodle database
 *
 * @return array An array of objects containing all the courses
 */
function get_courses_enrolment_count()
{
    global $DB;
    global $CFG;
    $enrolTable = $CFG->prefix . "enrol";
    $user_enrolmentsTable = $CFG->prefix . "user_enrolments";
    $courseTable = $CFG->prefix . "course";

    $courses = $DB->get_records_sql("
        SELECT courseid, fullname, startdate, enddate, enrolments
        FROM $courseTable,
           (
                SELECT courseid, sum(nr) as enrolments
                FROM $enrolTable,
                    (
                         SELECT enrolid, count(enrolid) as nr
                         FROM $user_enrolmentsTable
                         GROUP BY enrolid
                    ) as counts
                WHERE enrolid = id
                GROUP BY courseid
           ) as enrol_count
        WHERE $courseTable.id = courseid
        AND format = 'elevated'
        ");

    return $courses;
}

/**
 * Get a list of the course topic names of a specifc course from the moodle database
 *
 * @param int $courseid The id of the course to get the topics of
 * @return array An array of strings containing the course topic names
 */
function get_course_topics($courseid)
{
    global $DB;
    $topicData = $DB->get_records("course_sections", array('course' => $courseid), '', "section, name");
    $topics = array_map('get_topic_name', $topicData);
    return $topics;
}

/**
 * Get the name of a course topic
 *
 * @param object $topic A row from the moodle database (course_sections) containing at least the name and section of the topic
 * @return string The actual topic name
 */
function get_topic_name($topic)
{

    if ($topic->name != null) {
        return $topic->name;
    }

    if ($topic->section == "0") {
        return "General";
    }

    return "Topic " . $topic->section;
}

/**
 * Get the amount of emodules in a specific course from the moodle database
 *
 * @param int $courseid id of the course to get the count from
 * @return int The amount of emodules in the course
 */
function get_emodule_count($courseid)
{
    global $DB;
    $count = $DB->count_records('course_modules', array('course' => $courseid));
    return $count;
}

/**
 * Get an array of all the language strings in the boxdashboard plugin language. 'lang_' will be prepended to each language key to prevent conflicts when rendering a template.
 *
 * @return array An associative array containing al the language strings.
 */
function get_entire_language()
{
    require "config.php";                                                                //True to disable cache for debug
    $lang = get_string_manager()->load_component_strings($internalName, current_language(), true);
    $keys = array_map(function ($name) {
        return "lang_$name";
    }, array_keys($lang));
    $result = array_combine($keys, array_values($lang));
    return $result;
}

/**
 * From a specific e-module, get basic relevant information (section, section_name, module_type, module_name)
 *
 * @param int $id the id of the e-module
 * @return array An associative array containing the information
 */
function get_module_info($id)
{
    global $DB;
    $course_module = $DB->get_record("course_modules", array('id' => $id));
    if ($course_module == null) {
        return null;
    }
    $course_section = $DB->get_record("course_sections", array('id' => $course_module->section));
    $section_name = get_topic_name($course_section);
    $module_type = $DB->get_record("modules", array('id' => $course_module->module));
    $instance = $DB->get_record($module_type->name, array('id' => $course_module->instance));
    return array(
        "id" => $id,
        "section" => intval($course_module->section),
        "section_name" => $section_name,
        "module_type" => $module_type->name,
        "module_name" => $instance->name
    );
}

/**
 * Checks if the current user is logged in and is teacher or manager of any course (or the frontpage context)
 * or if the user is an admin at system context level.
 * If the current user doesn't meet this an Exception is thrown
 *
 * @return mixed depending if user has the right capabilities (void) or not (exception)
 * @throws coding_exception
 * @throws require_login_exception
 * @throws moodle_exception
 * @throws required_capability_exception
 */
function get_courselist_authorization()
{
    require_login();
    $systemcapability = 'local/boxdashboard:view';
    $systemcontext = context_system::instance();
    $coursecapability = 'local/boxdashboard:boxdashboard';
    $courses = get_courses();
    $courseids = array_column($courses, 'id');
    $courseidsint =  array_map(function ($course_id) {
        return (int) ($course_id);
    }, $courseids);

    $coursecontexts =  array_map(function ($course_id) {
        return context_course::instance($course_id);
    }, $courseidsint);

    $truesfalse =  array_map(function ($coursecontext) use ($coursecapability) {
        return (has_capability($coursecapability, $coursecontext));
    }, $coursecontexts);

    if (!has_capability($systemcapability, $systemcontext)) {
        if (!in_array(true, $truesfalse)) {
            throw new required_capability_exception($coursecontexts[0], 'local/boxdashboard:boxdashboard', 'nopermissions', '');
        }
    }
}

/**
 * Checks if the current user is logged in and is teacher or manager of a specific course
 * If the current user doesn't meet this an Exception is thrown
 *
 * @param int $courseID The ID of the course to be checked url
 * @return mixed depending if user has the right capabilities (void) or not (exception)
 * @throws coding_exception
 * @throws require_login_exception
 * @throws moodle_exception
 * @throws required_capability_exception
 */
function get_dashboard_authorization($courseID)
{
    require_login();
    require_capability('local/boxdashboard:boxdashboard', context_course::instance($courseID));
}

/**
 * Execute a django request
 *
 * @param string $request The request to execute
 * @param string $data If null, request will be GET, otherwise, request will be POST and $data will be the body.
 * @return array A nested (associative) array containing the json response
 */
function django_request($request, $data = null)
{
    $requester = new DjangoRequester();
    $reply = $requester->request($request, $data);
    return json_decode($reply, true, 512);
}

/**
 * Extract the id parameter from a url.
 *
 * @param string $url The url to extract the id from
 * @return int The id if present in the url, otherwise -1
 */
function getIdFromURL($url)
{
    $query = parse_url($url, PHP_URL_QUERY);
    if ($query == null) {
        return -1;
    }
    parse_str($query, $params);
    if (!isset($params['id'])) {
        return -1;
    }
    return intval($params['id']);
}
