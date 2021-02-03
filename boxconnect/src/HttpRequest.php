<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

interface HttpRequest
{
    public function setOpt($name, $value);
    public function exec();
    public function getInfo($name);
    public function errNo();
    public function error();
    public function close();
}

class CurlRequest implements HttpRequest
{
    private $request = null;

    public function __construct($url)
    {
        $this->request = curl_init($url);
    }

    public function setOpt($name, $value)
    {
        curl_setopt($this->request, $name, $value);
    }

    public function exec()
    {
        return curl_exec($this->request);
    }

    public function getInfo($name)
    {
        return curl_getinfo($this->request, $name);
    }

    public function errNo()
    {
        return curl_errno($this->request);
    }

    public function error()
    {
        return curl_error($this->request);
    }

    public function close()
    {
        curl_close($this->request);
    }
}
