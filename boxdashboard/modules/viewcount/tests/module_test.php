<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * Unit tests for the viewcount module
 *
 * @package local_boxdashboard.modules.viewcount
 * @author Joep
 */

use PHPUnit\Framework\TestCase;

// @codeCoverageIgnoreStart

require_once __DIR__ . '/../module.php';
require_once __DIR__ . '/../../../PHPmock.php';


class ViewcountModuleTest extends TestCase
{
    /**
     * Asserts that module_viewcount_getBlockData returns the data in the correct format
     * @covers ::module_viewcount_getBlockData
     */
    public function test_module_viewcount_getBlockData()
    {
        $func = new ReflectionFunction("module_viewcount_getBlockData");
        $patch = new FunctionPatch($func);
        $patch->addMock("module_viewcount_getGraphData");
        eval($patch->code);

        $res = module_viewcount_getBlockData_patch(0);
        $correct = ["graphs" => ["data" => "graphdata"]];

        $this->assertEquals($correct, $res);
    }

    /**
     * Asserts that module_viewcount_getDetailsData returns the data in the correct format
     * @covers ::module_viewcount_getDetailsData
     */
    public function test_module_viewcount_getDetailsData()
    {
        $func = new ReflectionFunction("module_viewcount_getDetailsData");
        $patch = new FunctionPatch($func);
        $patch->addMock("module_viewcount_getSimpleCount");
        $patch->addMock("module_viewcount_getGraphData");
        eval($patch->code);

        $res = module_viewcount_getDetailsData_patch(0);
        $correct = [
            "count" => 10,
            "graphs" => ["data" => "graphdata"]
        ];

        $this->assertEquals($correct, $res);
    }

    /**
     * Asserts that module_viewcount_getSimpleCount returns the data in the correct format
     * @covers ::module_viewcount_getSimpleCount
     */
    public function test_module_viewcount_getSimpleCount()
    {
        $func = new ReflectionFunction("module_viewcount_getSimpleCount");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock("django_request", "django_request_count_mock");
        eval($patch->code);

        $res = module_viewcount_getSimpleCount_patch(0);
        $correct = ["count" => 10];

        $this->assertEquals($correct, $res);
    }

    /**
     * Asserts that module_viewcount_getGraphData returns the correct data in the
     * correct format.
     * @covers ::module_viewcount_getGraphData
     */
    public function test_module_viewcount_getGraphData()
    {
        $func = new ReflectionFunction("module_viewcount_getGraphData");
        $patch = new FunctionPatch($func);
        $patch->addNamedMock("django_request", "django_request_history_mock");
        $patch->addNamedMock("get_module_info", "get_module_info_2_mock");
        eval($patch->code);

        $res = module_viewcount_getGraphData_patch(0);
        $correct = ["graphs" => [
            [
                "id" => 3,
                "points" => [
                    [
                        "date" => "2020-12-02",
                        "count" => 1
                    ],
                    [
                        "date" => "2020-11-13",
                        "count" => 1
                    ]
                ]
            ],
            [
                "id" => 1,
                "points" => [
                    [
                        "date" => "2020-12-02",
                        "count" => 1
                    ],
                    [
                        "date" => "2020-11-19",
                        "count" => 79
                    ],
                    [
                        "date" => "2020-11-18",
                        "count" => 19
                    ],
                    [
                        "date" => "2020-11-13",
                        "count" => 1
                    ],
                    [
                        "date" => "2020-11-12",
                        "count" => 1
                    ]
                ]
            ],
            [
                "id" => 5,
                "points" => [
                    [
                        "date" => "2020-12-02",
                        "count" => 2
                    ],
                    [
                        "date" => "2020-11-13",
                        "count" => 1
                    ]
                ]
            ]
        ]];

        $this->assertEquals($correct, $res);
    }
}


//----------------------------
//      Mock Functions
//----------------------------

function module_viewcount_getGraphData_mock()
{
    return ["graphs" => ["data" => "graphdata"]];
}

function module_viewcount_getSimpleCount_mock()
{
    return ["count" => 10];
}

function django_request_count_mock()
{
    return ["count" => 10];
}

function django_request_history_mock()
{
    return [
        "http://localhost/mod/page/view.php?id=3" => [
            [
                "date" => "2020-12-02",
                "count" => 1
            ],
            [
                "date" => "2020-11-13",
                "count" => 1
            ]
        ],
        "http://localhost/mod/page/view.php?id=1" => [
            [
                "date" => "2020-12-02",
                "count" => 1
            ],
            [
                "date" => "2020-11-19",
                "count" => 79
            ],
            [
                "date" => "2020-11-18",
                "count" => 19
            ],
            [
                "date" => "2020-11-13",
                "count" => 1
            ],
            [
                "date" => "2020-11-12",
                "count" => 1
            ]
        ],
        "http://localhost/mod/page/view.php?id=5" => [
            [
                "date" => "2020-12-02",
                "count" => 2
            ],
            [
                "date" => "2020-11-13",
                "count" => 1
            ]
        ]
    ];
}

function get_module_info_2_mock($id)
{
    return [
        "id" => $id
    ];
}

// @codeCoverageIgnoreEnd
