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

namespace src\transformer\events\mod_page;

defined('MOODLE_INTERNAL') || die();

use src\transformer\utils as utils;

function course_module_viewed(array $config, \stdClass $event)
{
    $repo = $config['repo'];
    $user = $repo->read_record_by_id('user', $event->userid);
    $course = $repo->read_record_by_id('course', $event->courseid);
    $lang = utils\get_course_lang($course);
    $numOfStatements = 1; //If bigger than 1, this will send a bunch of statements with randomized timestamps instead. Should always be 1 in production environment.

    if ($numOfStatements > 1) {
        $statements = [];
        for ($i = 0; $i < $numOfStatements; $i++) {
            $statements[$i] = [
                'actor' => utils\get_user($config, $user),
                'verb' => [
                    'id' => 'http://id.tincanapi.com/verb/viewed',
                    'display' => [
                        $lang => 'viewed'
                    ],
                ],
                'object' => utils\get_activity\course_module(
                    $config,
                    $course,
                    $event->contextinstanceid,
                    'https://w3id.org/xapi/acrossx/activities/page'
                ),
                'timestamp' => utils\get_random_timestamp($event),
                'context' => [
                    'platform' => $config['source_name'],
                    'language' => $lang,
                    'extensions' => utils\extensions\base($config, $event, $course),
                    'contextActivities' => [
                        'grouping' => [
                            utils\get_activity\site($config),
                            utils\get_activity\course($config, $course),
                        ],
                        'category' => [
                            utils\get_activity\source($config),
                        ]
                    ],
                ]
            ];
        }
        return $statements;
    } else {
        return [[
            'actor' => utils\get_user($config, $user),
            'verb' => [
                'id' => 'http://id.tincanapi.com/verb/viewed',
                'display' => [
                    $lang => 'viewed'
                ],
            ],
            'object' => utils\get_activity\course_module(
                $config,
                $course,
                $event->contextinstanceid,
                'https://w3id.org/xapi/acrossx/activities/page'
            ),
            'timestamp' => utils\get_event_timestamp($event),
            'context' => [
                'platform' => $config['source_name'],
                'language' => $lang,
                'extensions' => utils\extensions\base($config, $event, $course),
                'contextActivities' => [
                    'grouping' => [
                        utils\get_activity\site($config),
                        utils\get_activity\course($config, $course),
                    ],
                    'category' => [
                        utils\get_activity\source($config),
                    ]
                ],
            ]
        ]];
    }
}