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

namespace src\transformer;

defined('MOODLE_INTERNAL') || die();

function get_event_information()
{
    // For each supported event, get the corresponding function and whether the event is enabled by default
    return [
        '\core\event\course_completed' => ['function' => 'core\course_completed', 'enabled_by_default' => false],
        '\core\event\course_viewed' => ['function' => 'core\course_viewed', 'enabled_by_default' => true],              // Also used for: MOFA inactivity check
        '\core\event\user_created' => ['function' => 'core\user_created', 'enabled_by_default' => true],
        '\core\event\user_enrolment_created' => ['function' => 'core\user_enrolment_created', 'enabled_by_default' => false],
        '\core\event\user_loggedin' => ['function' => 'core\user_loggedin', 'enabled_by_default' => false],
        '\core\event\user_loggedout' => ['function' => 'core\user_loggedout', 'enabled_by_default' => false],
        '\core\event\user_graded' => ['function' => 'core\user_graded', 'enabled_by_default' => true],
        '\core\event\course_module_completion_updated' => ['function' => 'core\course_module_completion_updated', 'enabled_by_default' => false],
        '\mod_assign\event\assessable_submitted' => ['function' => 'mod_assign\assignment_submitted', 'enabled_by_default' => true],
        '\mod_assign\event\submission_graded' => ['function' => 'mod_assign\assignment_graded', 'enabled_by_default' => true],

        // Events for updating the MOFA database
        '\core\event\course_created' => ['function' => 'core\course_created', 'enabled_by_default' => true], // Update Mofa database
        '\core\event\course_updated' => ['function' => 'core\course_updated', 'enabled_by_default' => true], // Update Mofa database
        '\core\event\course_deleted' => ['function' => 'core\course_deleted', 'enabled_by_default' => true], // Update Mofa database

        '\core\event\user_updated' => ['function' => 'core\user_updated', 'enabled_by_default' => true], // Update Mofa database
        '\core\event\user_deleted' => ['function' => 'core\user_deleted', 'enabled_by_default' => true], // Update Mofa database

        '\core\event\role_assigned' => ['function' => 'core\user_role_assigned', 'enabled_by_default' => true], // Update Mofa database
        '\core\event\role_unassigned' => ['function' => 'core\user_role_unassigned', 'enabled_by_default' => true], // Update Mofa database

        '\core\event\course_module_created' => ['function' => 'core\module_created', 'enabled_by_default' => true], // Update Mofa database
        '\core\event\course_module_updated' => ['function' => 'core\module_updated', 'enabled_by_default' => true], // Update Mofa database
        '\core\event\course_module_deleted' => ['function' => 'core\module_deleted', 'enabled_by_default' => true], // Update Mofa database

        '\mod_book\event\chapter_created' => ['function' => 'mod_book\chapter_created', 'enabled_by_default' => true], // Update Mofa database
        '\mod_book\event\chapter_updated' => ['function' => 'mod_book\chapter_updated', 'enabled_by_default' => true], // Update Mofa database
        '\mod_book\event\chapter_deleted' => ['function' => 'mod_book\chapter_deleted', 'enabled_by_default' => true], // Update Mofa database

        // Other MOFA events
        '\mod_quiz\event\attempt_submitted' => ['function' => 'mod_quiz\attempt_submitted\handler', 'enabled_by_default' => true], // Used for: MOFA feedback assistant
        '\mod_quiz\event\edit_page_viewed' => ['function' => 'mod_quiz\edit_page_viewed', 'enabled_by_default' => true], // Used for: MOFA retrieve quiz questions


        // Bigbluebuttonbn events
        '\mod_bigbluebuttonbn\event\activity_created' => ['function' => 'mod_bigbluebuttonbn\activity_created', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\activity_deleted' => ['function' => 'mod_bigbluebuttonbn\activity_deleted', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\activity_updated' => ['function' => 'mod_bigbluebuttonbn\activity_updated', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\activity_viewed' => ['function' => 'mod_bigbluebuttonbn\activity_viewed', 'enabled_by_default' => true],
        '\mod_bigbluebuttonbn\event\bigbluebuttonbn_activity_management_viewed' => ['function' => 'mod_bigbluebuttonbn\bigbluebuttonbn_activity_management_viewed', 'enabled_by_default' => true],
        '\mod_bigbluebuttonbn\event\live_session' => ['function' => 'mod_bigbluebuttonbn\live_session', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\meeting_created' => ['function' => 'mod_bigbluebuttonbn\meeting_created', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\meeting_ended' => ['function' => 'mod_bigbluebuttonbn\meeting_ended', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\meeting_joined' => ['function' => 'mod_bigbluebuttonbn\meeting_joined', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\meeting_left' => ['function' => 'mod_bigbluebuttonbn\meeting_left', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\recording_deleted' => ['function' => 'mod_bigbluebuttonbn\recording_deleted', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\recording_edited' => ['function' => 'mod_bigbluebuttonbn\recording_edited', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\recording_imported' => ['function' => 'mod_bigbluebuttonbn\recording_imported', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\recording_protected' => ['function' => 'mod_bigbluebuttonbn\recording_protected', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\recording_published' => ['function' => 'mod_bigbluebuttonbn\recording_published', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\recording_unprotected' => ['function' => 'mod_bigbluebuttonbn\recording_unprotected', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\recording_unpublished' => ['function' => 'mod_bigbluebuttonbn\recording_unpublished', 'enabled_by_default' => false],
        '\mod_bigbluebuttonbn\event\recording_viewed' => ['function' => 'mod_bigbluebuttonbn\recording_viewed', 'enabled_by_default' => true],

        // Other events
        '\mod_book\event\course_module_viewed' => ['function' => 'mod_book\course_module_viewed', 'enabled_by_default' => true],
        '\mod_book\event\chapter_viewed' => ['function' => 'mod_book\chapter_viewed', 'enabled_by_default' => true],
        '\mod_chat\event\course_module_viewed' => ['function' => 'mod_chat\course_module_viewed', 'enabled_by_default' => true],
        '\mod_choice\event\course_module_viewed' => ['function' => 'all\course_module_viewed', 'enabled_by_default' => true],
        '\mod_data\event\course_module_viewed' => ['function' => 'all\course_module_viewed', 'enabled_by_default' => true],
        '\mod_facetoface\event\cancel_booking' => ['function' => 'mod_facetoface\cancel_booking', 'enabled_by_default' => false],
        '\mod_facetoface\event\course_module_viewed' => ['function' => 'mod_facetoface\course_module_viewed', 'enabled_by_default' => true],
        '\mod_facetoface\event\signup_success' => ['function' => 'mod_facetoface\signup_success', 'enabled_by_default' => false],
        '\mod_facetoface\event\take_attendance' => ['function' => 'mod_facetoface\take_attendance', 'enabled_by_default' => false],
        '\mod_feedback\event\course_module_viewed' => ['function' => 'mod_feedback\course_module_viewed', 'enabled_by_default' => true],
        '\mod_feedback\event\response_submitted' => ['function' => 'mod_feedback\response_submitted\handler', 'enabled_by_default' => false],
        '\mod_folder\event\course_module_viewed' => ['function' => 'all\course_module_viewed', 'enabled_by_default' => true],
        '\mod_forum\event\course_module_viewed' => ['function' => 'mod_forum\course_module_viewed', 'enabled_by_default' => true],
        '\mod_forum\event\discussion_created' => ['function' => 'mod_forum\discussion_created', 'enabled_by_default' => false],
        '\mod_forum\event\discussion_viewed' => ['function' => 'mod_forum\discussion_viewed', 'enabled_by_default' => true],
        '\mod_forum\event\post_created' => ['function' => 'mod_forum\post_created', 'enabled_by_default' => false],
        '\mod_forum\event\user_report_viewed' => ['function' => 'mod_forum\user_report_viewed', 'enabled_by_default' => true],
        '\mod_glossary\event\course_module_viewed' => ['function' => 'all\course_module_viewed', 'enabled_by_default' => true],
        '\mod_imscp\event\course_module_viewed' => ['function' => 'all\course_module_viewed', 'enabled_by_default' => true],
        '\mod_lesson\event\course_module_viewed' => ['function' => 'mod_lesson\course_module_viewed', 'enabled_by_default' => true],
        '\mod_lesson\event\content_page_viewed' => ['function' => 'mod_lesson\content_page_viewed', 'enabled_by_default' => true],
        '\mod_lti\event\course_module_viewed' => ['function' => 'all\course_module_viewed', 'enabled_by_default' => true],
        '\mod_page\event\course_module_viewed' => ['function' => 'mod_page\course_module_viewed', 'enabled_by_default' => true],
        '\mod_quiz\event\course_module_viewed' => ['function' => 'mod_quiz\course_module_viewed', 'enabled_by_default' => true],
        '\mod_quiz\event\attempt_abandoned' => ['function' => 'mod_quiz\attempt_submitted\handler', 'enabled_by_default' => true],
        '\mod_quiz\event\attempt_started' => ['function' => 'mod_quiz\attempt_started', 'enabled_by_default' => false],
        '\mod_quiz\event\attempt_reviewed' => ['function' => 'mod_quiz\attempt_reviewed', 'enabled_by_default' => false],
        '\mod_quiz\event\attempt_submitted' => ['function' => 'mod_quiz\attempt_submitted\handler', 'enabled_by_default' => true],
        '\mod_quiz\event\attempt_viewed' => ['function' => 'mod_quiz\attempt_viewed', 'enabled_by_default' => true],
        '\mod_resource\event\course_module_viewed' => ['function' => 'mod_resource\course_module_viewed', 'enabled_by_default' => true],
        '\mod_scorm\event\course_module_viewed' => ['function' => 'mod_scorm\course_module_viewed', 'enabled_by_default' => true],
        '\mod_scorm\event\sco_launched' => ['function' => 'mod_scorm\sco_launched', 'enabled_by_default' => false],
        '\mod_scorm\event\scoreraw_submitted' => ['function' => 'mod_scorm\scoreraw_submitted', 'enabled_by_default' => false],
        '\mod_scorm\event\status_submitted' => ['function' => 'mod_scorm\status_submitted', 'enabled_by_default' => false],
        '\mod_survey\event\course_module_viewed' => ['function' => 'mod_survey\course_module_viewed', 'enabled_by_default' => true],
        '\mod_url\event\course_module_viewed' => ['function' => 'mod_url\course_module_viewed', 'enabled_by_default' => true],
        '\mod_wiki\event\course_module_viewed' => ['function' => 'all\course_module_viewed', 'enabled_by_default' => true],
        '\mod_workshop\event\course_module_viewed' => ['function' => 'all\course_module_viewed', 'enabled_by_default' => true],
        '\totara_program\event\program_assigned' => ['function' => 'totara_program\program_assigned', 'enabled_by_default' => false]
    ];
}
