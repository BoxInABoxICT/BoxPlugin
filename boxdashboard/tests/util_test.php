<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * This file contains some utility functions used throughout the boxdashboard plugin.
 *
 * @package local_boxdashboard.testing
 * @author Joep
 */

use PHPUnit\Framework\TestCase;

// @codeCoverageIgnoreStart

require_once __DIR__ . '/../util.php';
require_once __DIR__ . '/../PHPmock.php';

/**
 * @codeCoverageIgnore
 */
class boxdashboardUtilTest extends TestCase
{
    /**
     * Asserts that get_courses_enrolment_count() returns the data correctly
     * and in the correct format.
     * @covers ::get_courses_enrolment_count()
     */
    public function test_get_courses_enrolment_count()
    {
        $func = new ReflectionFunction("get_courses_enrolment_count");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock('$CFG->prefix', "\"mdl_\"");
        $patch->addNamedMock('$DB->get_records_sql', "db_get_records_sql_mock");
        eval($patch->code);

        $res = get_courses_enrolment_count_patch();
        $correct = [
            ["courseid" => 12, "fullname" => "Testcursus", "startdate" => 1604942800, "enddate" => 1636298800, "enrolments" => 52],
            ["courseid" => 35, "fullname" => "Software Project", "startdate" => 1604912800, "enddate" => 1636198800, "enrolments" => 12]
        ];

        $this->assertEquals($correct, $res);
    }

    /**
     * Asserts that get_course_topics() returns the data correctly
     * and in the correct format.
     * @covers ::get_course_topics()
     */
    public function test_get_course_topics()
    {
        $func = new ReflectionFunction("get_course_topics");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock('$DB->get_records', "db_get_records_course_topics_mock");
        eval($patch->code);

        $res = get_course_topics_patch(0);
        $correct = ["General", "Topic 35", "Topic 22"];

        $this->assertEquals($correct, $res);
    }

    /**
     * Asserts that get_topic_name() returns the data correctly
     * and in the correct format.
     * @covers ::get_topic_name()
     */
    public function test_get_topic_name()
    {
        $func = new ReflectionFunction("get_topic_name");
        $patch = new FunctionPatch($func);
        eval($patch->code);

        $res = get_topic_name_patch((object)["section" => "0", "name" => null]);
        $res2 = get_topic_name_patch((object)["section" => "12", "name" => null]);
        $correct = "General";
        $correct2 = "Topic 12";

        $this->assertEquals($correct, $res);
        $this->assertEquals($correct2, $res2);
    }

    /**
     * Asserts that get_emodule_count() returns the data correctly
     * and in the correct format.
     * @covers ::get_emodule_count()
     */
    public function test_get_emodule_count()
    {
        $func = new ReflectionFunction("get_emodule_count");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock('$DB->count_records', "db_count_records_mock");
        eval($patch->code);

        $res = get_emodule_count_patch(0);
        $correct = 9;

        $this->assertEquals($correct, $res);
    }

    /**
     * Asserts that get_entire_language() returns the data correctly
     * and in the correct format.
     * @covers ::get_entire_language()
     */
    public function test_get_entire_language()
    {
        $func = new ReflectionFunction("get_entire_language");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock("require \"config.php\"", "");
        $patch->addNamedMock("get_string_manager()->load_component_strings(\$internalName, current_language(), true)", "load_component_strings_mock()");
        eval($patch->code);

        $res = get_entire_language_patch();
        $correct = ["lang_pluginname" => "boxdashboard", "lang_displayname" => "Statistics", "lang_display" => "Display"];

        $this->assertEquals($correct, $res);
    }

    /**
     * Asserts that get_module_info() returns the data correctly
     * and in the correct format.
     * @covers ::get_module_info()
     */
    public function test_get_module_info()
    {
        $func = new ReflectionFunction("get_module_info");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock('$DB->get_record', "db_get_record_module_info_mock");
        eval($patch->code);

        $res = get_module_info_patch(12);
        $correct = ["id" => "12", "section" => "8", "section_name" => "Name", "module_type" => "Name", "module_name" => "Name"];

        $this->assertEquals($correct, $res);
    }

    /**
     * Asserts that get_courselist_authorization() returns the data correctly
     * and in the correct format.
     * @covers ::get_courselist_authorization()
     */
    public function test_get_courselist_authorization()
    {
        $func = new ReflectionFunction("get_courselist_authorization");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock('require_login()', "");
        $patch->addNamedMock('context_system::instance();', "");
        $patch->addMock('get_courses');
        $patch->addNamedMock('context_course::instance($course_id)', "");
        $patch->addMock('has_capability');

        eval($patch->code);

        $res = get_courselist_authorization_patch();
        $correct = null;

        $this->assertEquals($correct, $res);
    }

     /**
     * Asserts that get_dashboard_authorization() returns the data correctly
     * and in the correct format.
     * @covers ::get_dashboard_authorization()
     */
    public function test_get_dashboard_authorization()
    {
        $func = new ReflectionFunction("get_dashboard_authorization");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock('require_login()', "");
        $patch->addMock('require_capability');
        $patch->addNamedMock('context_course::instance($courseID)', "");

        eval($patch->code);

        $res = get_dashboard_authorization_patch(1);
        $correct = null;

        $this->assertEquals($correct, $res);
    }

     /**
     * Asserts that django_request() returns the data correctly
     * and in the correct format.
     * @covers ::django_request()
     */
    public function test_django_request()
    {
        $func = new ReflectionFunction("django_request");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock('new DjangoRequester();', "");
        $patch->addNamedMock('$requester->request($request, $data)', "requester_django_request_mock()");

        eval($patch->code);

        $res = django_request_patch(1);
        $correct = [0 => "Hello, this is a response with the following arguments:"];

        $this->assertEquals($correct, $res);
    }

    /**
     * Asserts that getIdFromURL() returns the data correctly
     * and in the correct format.
     * @covers ::getIdFromURL()
     */
    public function test_getIdFromURL()
    {
        $func = new ReflectionFunction("getIdFromURL");
        $patch = new FunctionPatch($func);

        eval($patch->code);

        $res = getIdFromURL_patch("http://localhost/local/boxdashboard/dashboard.php?id=2");
        $correct = 2;

        $this->assertEquals($correct, $res);
    }
}


//----------------------------
//      Mock Functions
//----------------------------

function db_get_records_sql_mock()
{
    return [
        ["courseid" => 12, "fullname" => "Testcursus", "startdate" => 1604942800, "enddate" => 1636298800, "enrolments" => 52],
        ["courseid" => 35, "fullname" => "Software Project", "startdate" => 1604912800, "enddate" => 1636198800, "enrolments" => 12]
    ];
}

function db_get_records_course_topics_mock()
{
    return [
        0 => (object)["section" => "0", "name" => null],
        1 => (object)["section" => "35", "name" => null],
        2 => (object)["section" => "22", "name" => null]
    ];
}

function db_count_records_mock()
{
    return 9;
}

function load_component_strings_mock()
{
    return ["pluginname" => "boxdashboard", "displayname" => "Statistics", "display" => "Display"];
}

function db_get_record_module_info_mock()
{
    return (object)["section" => "8", "module" => "Module", "instance" => "Instance", "name" => "Name"];
}

function get_courses_mock()
{
        return [["id" => "9"]];
}

function has_capability_mock($capability, $context)
{
    return [true, false];
}

function require_capability_mock($capability)
{
    return Exception::class;
}

function requester_django_request_mock()
{
    return '{"0": "Hello, this is a response with the following arguments:"}';
}
// @codeCoverageIgnoreEnd
