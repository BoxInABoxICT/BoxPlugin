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

namespace src\transformer\events\core;

defined('MOODLE_INTERNAL') || die();
use src\transformer\utils as utils;

function user_updated(array $config, \stdClass $event)
{

    $repo = $config['repo'];
    $user = $repo->read_record_by_id('user', $event->relateduserid);
    $lang = $config['source_lang'];

    return [[
        'actor' => utils\get_user($config, $user),
        'verb' => [
            'id' => 'http://activitystrea.ms/schema/1.0/update',
            'display' => [
                $lang => 'updated'
            ],
        ],
        'object' => utils\get_activity\user($config, $user),
        'timestamp' => utils\get_event_timestamp($event),
        'context' => [
            'platform' => $config['source_name'],
            'language' => $lang,
            'extensions' => array_merge(utils\extensions\base($config, $event, null), utils\extensions\additional($config, $event, 'http://id.tincanapi.com/activitytype/update', $info = [
                        "firstname" => $user->firstname,
                        "lastname" => $user->lastname,
                        "username" => $user->username,
                        "email" => $user->email,
                        "id" => $user->id,
                    ])),
            'contextActivities' => [
                'category' => [
                    utils\get_activity\source($config)
                ]
            ],
        ]
    ]];
}
