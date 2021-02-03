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

namespace src\transformer\utils\get_activity;

defined('MOODLE_INTERNAL') || die();

use src\transformer\utils as utils;

/*
This function returns a page object. A page is contained in a lesson.
The page object contains an id (the URL to the page),
a definition (it's type and name),
and metadata which contains the ID's and names of the course, lesson and page.

To view the defined xAPI format of the metadata extension go to:
    THE_PLUGIN_LOCATION/xapi/extension-urls/content-page.html
*/

function content_page(array $config, $course, $page, $lesson, $cmid, $xapitype)
{
    //Get the database
    $repo = $config['repo'];

    //Retrieve the course module and its module object from the database
    $coursemodule = $repo->read_record_by_id('course_modules', $cmid);
    $module = $repo->read_record_by_id('modules', $coursemodule->module);

    //Reconstruct the URL of the page
    $contentpageurl = $config['app_url'] . '/mod/' . $module->name . '/view.php?id=' . $cmid . '&pageid=' . $page->id;
    //Get the language
    $courselang = utils\get_course_lang($course);

    //Create a page object with its URL, type and name
    $object = [
        'id' => $contentpageurl,
        'definition' => [
            'type' => $xapitype,
            'name' => [
                $courselang => $page->title,
            ],
        ],
    ];

    //Add the metadata containing ID's and names, the names are indexed per language
    $object['definition']['extensions']['file:///.../xapi/extension-urls/content-page.html'] =
    [
        'courseid' => $course->id,
        'lessonid' => $lesson->id,
        'pageid'   => $page->id,
        'coursename' => [
            $courselang => $course->fullname
        ],
        'lessonname' => [
            $courselang => $lesson->name
        ],
        'pagename' => [
            $courselang => $page->title
        ]
    ];

    return $object;
}
