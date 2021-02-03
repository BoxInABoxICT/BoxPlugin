<?php

// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

namespace src\transformer\events\mod_lesson;

defined('MOODLE_INTERNAL') || die();

use src\transformer\utils as utils;

/*
This function creates an LRS statement object when a page is viewed by the user.
The statement contains information concerning the actor, verb, page object and timestamp.
*/

function content_page_viewed(array $config, \stdClass $event)
{
    //Get the database
    $repo = $config['repo'];

    //Get the course, page and lesson and user from the database
    $course = $repo->read_record_by_id('course', $event->courseid);
    $page = $repo->read_record_by_id('lesson_pages', $event->objectid);
    $lesson = $repo->read_record_by_id('lesson', $page->lessonid);
    $user = $repo->read_record_by_id('user', $event->userid);

    //Retrieve the course language
    $lang = utils\get_course_lang($course);

    //Create an LRS statement object
    $statement = [[
        //Set actor to current user
        'actor' => utils\get_user($config, $user),
        //Set verb to viewed (viewed a page)
        'verb' => [
            'id' => 'http://id.tincanapi.com/verb/viewed',
            'display' => [
                $lang => 'viewed'
            ],
        ],
        //Set object to current page
        'object' => utils\get_activity\content_page(
            $config,
            $course,
            $page,
            $lesson,
            $event->contextinstanceid,
            'http://adlnet.gov/expapi/activities/page'
        ),
        //Set timestamp to current time
        'timestamp' => utils\get_event_timestamp($event)
    ]];

    return $statement;
}
