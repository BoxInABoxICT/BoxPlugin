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

defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig) {
    $ADMIN->add('localplugins', new admin_category('local_boxconnect_settings', new lang_string('pluginname', 'local_boxconnect')));
    $settingspage = new admin_settingpage('local_boxconnect', get_string('pluginname', 'local_boxconnect'));

    if ($ADMIN->fulltree) {
        //Django endpoint
        $settingspage->add(new admin_setting_configtext(
            'local_boxconnect/endpoint',
            get_string('endpoint', 'local_boxconnect'),
            '',
            'http://example.com/Django/base/endpoint',
            PARAM_URL
        ));
        //Django auth token
        $settingspage->add(new admin_setting_configtext(
            'local_boxconnect/token',
            get_string('token', 'local_boxconnect'),
            '',
            'Auth Token',
            PARAM_TEXT
        ));
    }

    $ADMIN->add('localplugins', $settingspage);
}
