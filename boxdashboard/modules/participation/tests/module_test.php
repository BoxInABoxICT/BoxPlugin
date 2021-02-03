<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * Unit tests for the participation module
 *
 * @package local_boxdashboard.modules.participation
 * @author Joep
 */

use PHPUnit\Framework\TestCase;

// @codeCoverageIgnoreStart

require_once __DIR__ . '/../module.php';
require_once __DIR__ . '/../../../PHPmock.php';

/**
 * @codeCoverageIgnore
 */
class ParticipationModuleTest extends TestCase
{
    /**
     * Asserts that module_participation_getBlockData returns the data in the correct format
     * @covers ::module_participation_getBlockData
     */
    public function test_module_participation_getBlockData()
    {
        $func = new ReflectionFunction("module_participation_getBlockData");
        $patch = new FunctionPatch($func);
        $patch->addMock("module_participation_getPageParticipation");
        eval($patch->code);

        $res = module_participation_getBlockData_patch(0);

        $this->assertEquals([
            "pageviews" => [
                "data" => "pageParticipation"
            ]
        ], $res);
    }

    /**
     * Asserts that module_participation_getDetailsData returns the data in the correct format
     * @covers ::module_participation_getDetailsData
     */
    public function test_module_participation_getDetailsData()
    {
        $func = new ReflectionFunction("module_participation_getDetailsData");
        $patch = new FunctionPatch($func);
        $patch->addMock("module_participation_getCompletion");
        $patch->addMock("module_participation_getPageParticipation");
        eval($patch->code);

        $res = module_participation_getDetailsData_patch(0);

        $this->assertEquals([
            "quizCompletion" => [
                "data" => "completiondata",
                "module" => "quiz",
                "analytics" => "quiz"
            ],
            "assignmentCompletion" => [
                "data" => "completiondata",
                "module" => "assign",
                "analytics" => "assignment"
            ],
            "pageviews" => [
                "data" => "pageParticipation"
            ]
        ], $res);
    }

    /**
     * Asserts that module_participation_getPageParticipation returns the data correctly
     * and in the correct format.
     * @covers ::module_participation_getPageParticipation
     */
    public function test_module_participation_getPageParticipation()
    {
        $func = new ReflectionFunction("module_participation_getPageParticipation");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock("django_request", "django_request_pageparticipation_mock");
        $patch->addMock("get_courses_enrolment_count");
        $patch->addNamedMock('$DB->get_records', "db_get_records_mock");
        $patch->addMock("get_module_info");
        eval($patch->code);

        $res = module_participation_getPageParticipation_patch(0);
        $correct = [
            ["id" => 1, "percentage" => 1],
            ["id" => 2, "percentage" => 0.5],
            ["id" => 3, "percentage" => 0.5],
            ["id" => 4, "percentage" => 0.3],
            ["id" => 5, "percentage" => 0],
            ["id" => 6, "percentage" => 0.7],
            ["id" => 7, "percentage" => 0]
        ];

        $this->assertEquals($correct, $res);
    }

    /**
     * Asserts that module_participation_getCompletion returns the correct results
     * in the correct format.
     * @covers ::module_participation_getCompletion
     */
    public function test_module_participation_getCompletion()
    {
        $func = new ReflectionFunction("module_participation_getCompletion");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock("django_request", "django_request_completion_mock");
        $patch->addMock("get_courses_enrolment_count");
        $patch->addNamedMock('$DB->get_records', 'db_get_records_mock');
        $patch->addNamedMock('$DB->get_record', 'db_get_record_mock');
        $patch->addMock('get_module_info');
        eval($patch->code);

        $res = module_participation_getCompletion_patch(0, "assignment", "assign");
        $correct = [
            ["id" => 1, "percentage" => 0],
            ["id" => 2, "percentage" => 0.3],
            ["id" => 3, "percentage" => 0.2],
            ["id" => 4, "percentage" => 0],
            ["id" => 5, "percentage" => 0.9],
            ["id" => 6, "percentage" => 0.5],
            ["id" => 7, "percentage" => 0]
        ];

        $this->assertEquals($correct, $res);
    }
}


//----------------------------
//      Mock Functions
//----------------------------

function module_participation_getPageParticipation_mock()
{
    return ["data" => "pageParticipation"];
}

function module_participation_getCompletion_mock($courseid, $analytics, $module)
{
    return [
        "data" => "completiondata",
        "module" => $module,
        "analytics" => $analytics
    ];
}

function django_request_pageparticipation_mock()
{
    return [
        "http://localhost/mod/resource/view.php?id=1" => 10,
        "http://localhost/mod/resource/view.php?id=2" => 5,
        "http://localhost/mod/forum/view.php?id=4" => 3,
        "http://localhost/mod/page/view.php?id=3" => 5,
        "http://localhost/mod/page/view.php?id=6" => 7,
    ];
}

function django_request_completion_mock()
{
    return [
        "http://localhost/mod/assign/view.php?id=3" => 2,
        "http://localhost/mod/assign/view.php?id=2" => 3,
        "http://localhost/mod/assign/view.php?id=6" => 5,
        "http://localhost/mod/assign/view.php?id=5" => 9
    ];
}

function get_courses_enrolment_count_mock()
{
    return [
        0 => (object)[
            "enrolments" => "10"
        ]
    ];
}

function db_get_record_mock()
{
    return (object) ["id" => 1234];
}

function db_get_records_mock()
{
    return [
        1 => null,
        2 => null,
        3 => null,
        4 => null,
        5 => null,
        6 => null,
        7 => null,
    ];
}

function get_module_info_mock($id)
{
    return [
        "id" => $id
    ];
}


// @codeCoverageIgnoreEnd
