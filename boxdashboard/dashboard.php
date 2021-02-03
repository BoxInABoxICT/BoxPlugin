<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * This file is responsible for collecting all the data from the modules, rendering it and then display the course statistics page for a specific course.
 *
 * @package local_boxdashboard
 * @author Joep
 */

//Get all required parameters/variables
require_once(__DIR__ . '/../../config.php');
global $DB;
global $USER;
require_once "config.php";
require_once "util.php";
$courseID = required_param('cid', PARAM_INT);
$course = $DB->get_record('course', ['id' => $courseID]);

//Check if user has correct capabilities to access the dashboard of this course
get_dashboard_authorization($courseID);

//DEBUG SETTING
$CFG->cachejs = false;


//----------------------------
//        Setup page
//----------------------------

$PAGE->set_url(new moodle_url("$pluginPath/dashboard.php"));
$PAGE->set_context(\context_system::instance());
$PAGE->navigation
    ->add(get_string('displayname', $internalName), new moodle_url("$pluginPath/courselist.php"))
    ->add($course->fullname, new moodle_url("$pluginPath/dashboard.php", array('cid' => $courseID)))
    ->make_active();

//Setup imorts
$PAGE->requires->css("$pluginPath/stylesheets/dashboard.css");
$PAGE->requires->jquery();
foreach ($stylesheets as $stylesheet) {
    $PAGE->requires->css("$pluginPath/stylesheets/$stylesheet");
}
foreach ($scripts as $script) {
    $PAGE->requires->js("$pluginPath/scripts/$script", true);
}

//----------------------------
//      Setup page data
//----------------------------
$lang = get_entire_language();
$blocks = render_blocks($OUTPUT, $PAGE, $USER->id, $course->id, $lang);
$participants = get_courses_enrolment_count()[$courseID]->enrolments;
$topics = count(get_course_topics($courseID));
$emodules = get_emodule_count($courseID);
$participation = 70;

$renderData = [
    'blocks' => $blocks,
    'topics' => $topics,
    'emodules' => $emodules,
    'participation' => $participation,
    'participants' => $participants,
    'coursename' => $course->fullname,
    'courseid' => $courseID,
    'hasStarted' =>  getdate()[0] > $course->startdate,
    'hasEnded' => getdate()[0] > $course->enddate && $course->enddate != 0
];
$renderData = array_merge($renderData, $lang);

//----------------------------
//      Render the page
//----------------------------

echo $OUTPUT->header("Course");
echo $OUTPUT->render_from_template("$internalName/dashboard", $renderData);
echo $OUTPUT->footer();

//=========================================================================================================

//----------------------------
//     Support Functions
//----------------------------

/**
 * Render all the blocks that should be displayed on the page
 *
 * @param $OUTPUT reference to the $OUTPUT variable
 * @param $PAGE reference to the $PAGE variable
 * @param int $userid the id of the user that views the course page
 * @param int $courseid the id of the course for which the data should be retrieved
 * @return array An array of html strings, each of the strings being the partial for one block.
 */
function render_blocks($OUTPUT, $PAGE, $userid, $courseid, $lang)
{
    require "config.php";

    //Render the required blocks
    $blocks = array();
    foreach ($installedModules as $key) {
        require("modules/" . $key . "/config.php");

        //Construct default block data and set default values
        $data = array(
            "blockname" => $fullname,
            "pluginPath" => $pluginPath,
        );
        $data = array_merge($data, $lang);

        //Pass the block data to the page and add the required files
        require("modules/$key/config.php");
        if ($blockJS) {
            $PAGE->requires->js("$pluginPath/modules/$key/block.js");
        }
        if ($blockCSS) {
            $PAGE->requires->css("$pluginPath/modules/$key/block.css");
        }
        if ($hasDetails && $detailJS) {
            $PAGE->requires->js("$pluginPath/modules/$key/details.js");
        }
        if ($hasDetails && $detailCSS) {
            $PAGE->requires->css("$pluginPath/modules/$key/details.css");
        }

        //Render the block and add it to the blocks array
        $contents = $OUTPUT->render_from_template("$internalName/modules/$key/block", $data);

        $dataArray =  (object)[
            'content' => $contents,
            'blockname' => $data["blockname"],
            'bid' => $key,
            'cid' => $courseid,
            'hasDetails' => $hasDetails,
            'desc' => $desc,
            'visualisationType' => $visualisationType
        ];

        if ($hasDetails) {
            $dataArray->detailsData = $OUTPUT->render_from_template("$internalName/modules/$key/details", $data);
        }

        array_push($blocks, $dataArray);
    }

    return $blocks;
}

/**
 * Get the settings the user has set for the visibility of each of the modules.
 *
 * @param int $userid the id of the user that views the page
 * @return object A single row from the database with the settings for each module for the specified user.
 */
function get_block_settings($userid)
{
    global $DB;
    require "config.php";
    //Get the settings from the database and set to default if non existent
    $settings = $DB->get_record($internalName . '_usersettings', array('userid' => $userid));
    if (!$settings) {
        $DB->insert_record($internalName . '_usersettings', (object)['userid' => $userid]);
        $settings = $DB->get_record($internalName . '_usersettings', array('userid' => $userid));
    }
    return $settings;
}
