<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * In this file, all the hooks for moodle can be added.
 *
 * @package local_boxdashboard
 * @author Joep
 */

//Include all the required files and variables
require_once "util.php";

/**
 * Hook on the extend_navigation function that adds the course statistics page to the navigation, but only if the user has the right capabilities
 */
function local_boxdashboard_extend_navigation(global_navigation $navigation)
{
    try {
        get_courselist_authorization();
      //Add page to navigation menu
        $navNode = $navigation->add("Course Statistics", new moodle_url("/local/boxdashboard/courselist.php"), null, null, null, new pix_icon('i/report', ''));
        $navNode->showinflatnavigation = true;
    } catch (moodle_exception $e) {
    }
}
