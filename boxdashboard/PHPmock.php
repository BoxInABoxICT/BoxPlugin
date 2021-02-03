<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * This file can be used to mock functions that are called in functions that are being tested
 *
 * @package local_boxdashboard.testing
 * @author Joep
 */

/**
 * Class used to create a patch of a specific function in which function calls can be mocked
 */
class FunctionPatch
{

    /**
     * Create a new patch function with the name originalName_patch
     *
     * @param ReflectionFunction $function A ReflectionFunction object of the function to patch
     */
    public function __construct($function)
    {
        $this->func = $function;
        $this->patch = $function->getName() . "_patch";
        $file = file($function->getFileName());
        $startline = $function->getStartLine() - 1;
        $endline = $function->getEndLine();
        $this->code = implode("", array_slice($file, $startline, $endline - $startline));
        $this->code =  str_replace($function->getName(), $this->patch, $this->code);
    }

    /**
     * Will replace a function call to functionName with a call to functionName_mock
     *
     * @param string $functionName The name of the function to mock
     */
    public function addMock($functionName)
    {
        $this->code = str_replace($functionName, $functionName . '_mock', $this->code);
    }

    /**
     * Will replace a function call to functionName with a call to mockName
     *
     * @param string $functionName The name of the function to mock
     * @param string $mockName The name of the mock function to call
     */
    public function addNamedMock($functionName, $mockName)
    {
        $this->code = str_replace($functionName, $mockName, $this->code);
    }
}
