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

namespace src\transformer\events\mod_quiz;

defined('MOODLE_INTERNAL') || die();
use src\transformer\utils as utils;

function edit_page_viewed(array $config, \stdClass $event)
{

    $repo = $config['repo'];
    $user = $repo->read_record_by_id('user', $event->userid);
    $course = $repo->read_record_by_id('course', $event->courseid);
    $lang = utils\get_course_lang($course);
    $unserializedquizid = unserialize($event->other);
    $quiz = $repo->read_record_by_id('quiz', intval($unserializedquizid['quizid']));
    $quiz_slots = $repo->read_records('quiz_slots', ['quizid' => $quiz->id]);
    $questions = [];
    foreach ($quiz_slots as $quiz_slot) {
        array_push($questions, utils\get_question_information($repo, $quiz_slot));
    }

    return [[
        'actor' => utils\get_user($config, $user),
        'verb' => [
            'id' => 'http://id.tincanapi.com/verb/viewed',
            'display' => [
                $lang => 'viewed'
            ],
        ],
        'object' => utils\get_activity\course_quiz_edit_page($config, $course, $event->contextinstanceid),
        'timestamp' => utils\get_event_timestamp($event),
        'context' => [
            'platform' => $config['source_name'],
            'language' => $lang,
            'extensions' => array_merge(utils\extensions\base($config, $event, $course), utils\extensions\additional($config, $event, 'http://activitystrea.ms/schema/1.0/question', $questions)),
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
