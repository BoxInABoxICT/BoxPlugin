<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * Unit tests for the studenttime module
 *
 * @package local_boxdashboard.modules.studenttime
 * @author
 */

use PHPUnit\Framework\TestCase;

// @codeCoverageIgnoreStart

require_once __DIR__ . '/../module.php';
require_once __DIR__ . '/../../../PHPmock.php';

class StudenttimeModuleTest extends TestCase
{

     /**
     * Asserts that module_studenttime_getBlockData() returns the data correctly
     * and in the correct format.
     * @covers ::module_studenttime_getBlockData()
     */
    public function test_module_studenttime_getBlockData()
    {
        $func = new ReflectionFunction("module_studenttime_getBlockData");
        $patch = new FunctionPatch($func);
        $patch->addMock('module_studenttime_getGraphData');

        eval($patch->code);

        $res = module_studenttime_getBlockData_patch(1);
        $correct = [
            "graphs" => [0 => [0 => ["id" => 4, "section" => 2, "section_name" => "Topic 1", "module_type" => "page", "module_name" => "Page 2"], "points" => [0 => ["date" => "2020-11-17", "time" => 37.0, "count" => 1]]]]
        ];

        $this->assertEquals($correct, $res);
    }

    /**
     * Asserts that module_studenttime_getGraphData() returns the data correctly
     * and in the correct format.
     * @covers ::module_studenttime_getGraphData()
     */
    public function test_module_studenttime_getGraphData()
    {
        $func = new ReflectionFunction("module_studenttime_getGraphData");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock("django_request", "django_request_time_mock");
        $patch->addNamedMock("get_module_info", "get_module_info_time_mock");

        eval($patch->code);

        $res = module_studenttime_getGraphData_patch(1);
        $correct = ["graphs" => [0 => [0 => ["id" => 4, "section" => 2, "section_name" => "Topic 1", "module_type" => "page", "module_name" => "Page 2"], "points" => [0 => ["date" => "2020-11-17", "time" => 37.0, "count" => 1]]]]];

        $this->assertEquals($correct, $res);
    }
}


//----------------------------
//      Mock Functions
//----------------------------

function django_request_time_mock()
{
    return ["http://localhost/mod/page/view.php?id=4" => [0 => ["date" => "2020-11-17", "time" => 37.0, "count" => 1]]];
}

function get_module_info_time_mock()
{
    return [0 => ["id" => 4, "section" => 2, "section_name" => "Topic 1", "module_type" => "page", "module_name" => "Page 2"]];
}

function module_studenttime_getGraphData_mock($courseid)
{
    return ["graphs" => [0 => [0 => ["id" => 4, "section" => 2, "section_name" => "Topic 1", "module_type" => "page", "module_name" => "Page 2"], "points" => [0 => ["date" => "2020-11-17", "time" => 37.0, "count" => 1]]]]];
}

// @codeCoverageIgnoreEnd
