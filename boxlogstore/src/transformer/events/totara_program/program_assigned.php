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

namespace src\transformer\events\totara_program;

defined('MOODLE_INTERNAL') || die();

use src\transformer\utils as utils;

function program_assigned(array $config, \stdClass $event)
{
    $repo = $config['repo'];
    $user = $repo->read_record_by_id('user', $event->userid);
    $program = $repo->read_record_by_id('prog', $event->objectid);
    $lang = $config['source_lang'];

    return[[
        'actor' => utils\get_user($config, $user),
        'verb' => [
            'id' => 'http://activitystrea.ms/schema/1.0/assign',
            'display' => [
                $lang => 'assigned'
            ],
        ],
        'object' => utils\totara\program($config, $program, $lang),
        'timestamp' => utils\get_event_timestamp($event),
        'context' => [
            'platform' => $config['source_name'],
            'language' => $lang,
            'extensions' => utils\extensions\base($config, $event),
            'contextActivities' => [
                'grouping' => [
                    utils\get_activity\site($config)
                ],
                'category' => [
                    utils\get_activity\source($config)
                ]
            ],
        ]
    ]];
}