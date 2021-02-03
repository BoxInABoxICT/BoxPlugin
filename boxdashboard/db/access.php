<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.


defined('MOODLE_INTERNAL') || die();
/* The currently set capabilities for the boxdashboard plugin
* local/boxdashboard:view is for the capabilities for the different roles that match the archetypes (manager) on system context level.
* local/boxdashboard:boxdashboard is for the capabilities for the different roles that match the archetypes (manager and editingteacher) on course context level.
*/
$capabilities = array(

    'local/boxdashboard:view' => array(
        'captype' => 'read',
        'contextlevel' => CONTEXT_SYSTEM,
        'archetypes' => array(
            'manager' => CAP_ALLOW
        ),

    ),

    'local/boxdashboard:boxdashboard' => array(
        'captype' => 'read',
        'contextlevel' => CONTEXT_COURSE,
        'archetypes' => array(
            'editingteacher' => CAP_ALLOW,
            'manager' => CAP_ALLOW
        )
    )

);
