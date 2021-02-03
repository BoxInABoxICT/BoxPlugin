<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * Unit tests for the participation module
 *
 * @package local_boxdashboard.modules.dtpageviews
 * @author Joep
 */

use PHPUnit\Framework\TestCase;

// @codeCoverageIgnoreStart

require_once __DIR__ . '/../module.php';
require_once __DIR__ . '/../../../PHPmock.php';

/**
 * @codeCoverageIgnore
 */
class PageviewsModuleTest extends TestCase
{
 /**
     * Asserts that module_dtpageviews_getBlockData returns the result in the correct format
     * @covers ::module_dtpageviews_getBlockData
     */
    public function test_module_dtpageviews_getBlockData()
    {
        $func = new ReflectionFunction('module_dtpageviews_getBlockData');
        $patch = new FunctionPatch($func);
        $patch->addMock("django_request");
        $patch->addMock("module_dtpageviews_getCourseScenarios");
        eval($patch->code);

        $res = module_dtpageviews_getBlockData_patch(0);

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
}


//----------------------------
//      Mock Functions
//----------------------------

function module_dtpageviews_getCourseScenarios_mock($courseid)
{
    return [1, 2, 3];
}

// @codeCoverageIgnoreEnd
