<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * The version file for the boxdashboard plugin
 *
 * @package local_boxdashboard
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'local_boxdashboard';
$plugin->version = 2020071904;
$plugin->requires = 2016052300;

$plugin->dependencies = [
    'local_boxconnect' => 2020091901
];
