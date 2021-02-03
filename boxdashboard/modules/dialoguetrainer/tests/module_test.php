<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * Unit tests for the dialoguetrainer module
 *
 * @package local_boxdashboard.modules.dialoguetrainer
 * @author Joep
 */

use PHPUnit\Framework\TestCase;

// @codeCoverageIgnoreStart

require_once __DIR__ . '/../module.php';
require_once __DIR__ . '/../../../PHPmock.php';


class DTModuleTest extends TestCase
{
    /**
     * Asserts that module_dialoguetrainer_getBlockData returns the result in the correct format
     * @covers ::module_dialoguetrainer_getBlockData
     */
    public function test_module_dialoguetrainer_getBlockData()
    {
        $func = new ReflectionFunction('module_dialoguetrainer_getBlockData');
        $patch = new FunctionPatch($func);
        $patch->addMock("module_dialoguetrainer_getCourseScenarios");
        $patch->addMock("django_request");
        eval($patch->code);

        $res = module_dialoguetrainer_getBlockData_patch(0);

        $this->assertEquals(["scenarios" => [
            [
                "data" => "testResult",
                "id" => 1
            ],
            [
                "data" => "testResult",
                "id" => 2
            ],
            [
                "data" => "testResult",
                "id" => 3
            ],
        ]], $res);
    }

    /**
     * Assert that module_dialoguetrainer_getDetailsData returns the results in the correct format
     * @covers ::module_dialoguetrainer_getDetailsData
     */
    public function test_module_dialoguetrainer_getDetailsData()
    {
        $func = new ReflectionFunction('module_dialoguetrainer_getDetailsData');
        $patch = new FunctionPatch($func);
        $patch->addMock("module_dialoguetrainer_getCourseScenarios");
        $patch->addMock("module_dialoguetrainer_getDialogueTrainerAnalytics");
        eval($patch->code);

        $res = module_dialoguetrainer_getDetailsData_patch(0);

        $this->assertEquals([
            "scenarios" => [
                1 => "data1",
                2 => "data2",
                3 => "data3"
            ]
        ], $res);
    }

    /**
     * Assert that getDialogueTrainerAnalytics returns the results in the correct format
     * @covers ::module_dialoguetrainer_getDialogueTrainerAnalytics
     */
    public function test_module_dialoguetrainer_getDialogueTrainerAnalytics()
    {
        $func = new ReflectionFunction('module_dialoguetrainer_getDialogueTrainerAnalytics');
        $patch = new FunctionPatch($func);
        $patch->addMock("django_request");
        eval($patch->code);

        $res = module_dialoguetrainer_getDialogueTrainerAnalytics_patch(0);

        $this->assertEquals($res, [
            "betweenStudents" => ["data" => "testResult"],
            "betweenAttempts" => ["data" => "testResult"]
        ]);
    }
}


//----------------------------
//      Mock Functions
//----------------------------

function module_dialoguetrainer_getCourseScenarios_mock($courseid)
{
    return [1, 2, 3];
}

function module_dialoguetrainer_getDialogueTrainerAnalytics_mock($query)
{
    return "data$query";
}

function django_request_mock($query)
{
    return ["data" => "testResult"];
}

// @codeCoverageIgnoreEnd
