<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

use PHPUnit\Framework\TestCase;

require_once __DIR__ . '/../src/DjangoRequester.php';

define('MOODLE_INTERNAL');

class DjangoRequesterTest extends TestCase
{
    /**
     * Asserts the Requester will return the message body if response code is 200 OK
     * @covers \DjangoRequester
     */
    public function testStandardRequestResponse()
    {
        $requesterStub = $this->getMockBuilder('DjangoRequester')
            ->disableOriginalConstructor()
            ->disableOriginalClone()
            ->disableArgumentCloning()
            ->disallowMockingUnknownTypes()
            ->getMock();

        $CurlRequestMock = $this
            ->getMockBuilder('HttpRequest')
            ->setMethods(['setOpt', 'exec', 'getInfo', 'errNo', 'error', 'close'])
            ->getMock();

        $CurlRequestMock
            ->expects($this->any())
            ->method('exec')
            ->willReturn('messageBody');

        $CurlRequestMock
            ->expects($this->any())
            ->method('getInfo')
            ->willReturn(200);

        $CurlRequestMock
            ->expects($this->any())
            ->method('errNo')
            ->willReturn(0);

        $CurlRequestMock
            ->expects($this->any())
            ->method('error')
            ->willReturn('');

        $CurlRequestMock
            ->expects($this->exactly(1))
            ->method('close');

        $reflector = new ReflectionClass('DjangoRequester');
        $method = $reflector->getMethod('requestCall');
        $method->setaccessible(true);

        $reply = $method->invokeArgs($requesterStub, array("mockurl", $CurlRequestMock, null));
        $this->assertEquals('messageBody', $reply);
    }

    /**
     * Asserts the Requester will throw an exception if response code is anything other than 200 OK
     * @covers \DjangoRequester
     */
    public function testRequestHasNonOkResponseAndThrowsException()
    {
        $requesterStub = $this->getMockBuilder('DjangoRequester')
            ->disableOriginalConstructor()
            ->disableOriginalClone()
            ->disableArgumentCloning()
            ->disallowMockingUnknownTypes()
            ->getMock();

        $CurlRequestMock = $this
            ->getMockBuilder('HttpRequest')
            ->setMethods(['setOpt', 'exec', 'getInfo', 'errNo', 'error', 'close'])
            ->getMock();

        $CurlRequestMock
            ->expects($this->exactly(1))
            ->method('exec')
            ->willReturn('messageBody');

        $CurlRequestMock
            ->expects($this->any())
            ->method('getInfo')
            ->willReturn(401);

        $CurlRequestMock
            ->expects($this->any())
            ->method('errNo')
            ->willReturn(22);

        $CurlRequestMock
            ->expects($this->any())
            ->method('error')
            ->willReturn(new Exception('The requested URL returned error: 401 Unauthorized'));

        $CurlRequestMock
            ->expects($this->exactly(1))
            ->method('close');

        $reflector = new ReflectionClass('DjangoRequester');
        $method = $reflector->getMethod('requestCall');
        $method->setaccessible(true);

        $this->expectException(Exception::class);
        $reply = $method->invokeArgs($requesterStub, array("mockurl", $CurlRequestMock, null));
    }

    /**
     * Asserts the Requester will return different messages in different requests
     * @covers \DjangoRequester
     */
    public function testConsecutiveRequests()
    {
        $requesterStub = $this->getMockBuilder('DjangoRequester')
            ->disableOriginalConstructor()
            ->disableOriginalClone()
            ->disableArgumentCloning()
            ->disallowMockingUnknownTypes()
            ->getMock();

        $CurlRequestMock = $this
            ->getMockBuilder('HttpRequest')
            ->setMethods(['setOpt', 'exec', 'getInfo', 'errNo', 'error', 'close'])
            ->getMock();

        $CurlRequestMock
            ->expects($this->exactly(2))
            ->method('exec')
            ->willReturnOnConsecutiveCalls(...["Request1 Reply", "Request2 Reply"]);

        $CurlRequestMock
            ->expects($this->any())
            ->method('getInfo')
            ->willReturn(200);

        $CurlRequestMock
            ->expects($this->any())
            ->method('errNo')
            ->willReturn(0);

        $CurlRequestMock
            ->expects($this->any())
            ->method('error')
            ->willReturn('');

        $CurlRequestMock
            ->expects($this->exactly(2))
            ->method('close');

        $reflector = new ReflectionClass('DjangoRequester');
        $method = $reflector->getMethod('requestCall');
        $method->setaccessible(true);

        $reply = $method->invokeArgs($requesterStub, array("mockurl", $CurlRequestMock, null));
        $this->assertEquals('Request1 Reply', $reply);

        $reply = $method->invokeArgs($requesterStub, array("mockurl", $CurlRequestMock, null));
        $this->assertEquals('Request2 Reply', $reply);
    }

    /**
     * Asserts the wrapper function to verify the curlRequest gets constructed correctly
     * @covers \DjangoRequester
     */
    public function testTestWrapperFunction()
    {
        $requesterStub = $this->getMockBuilder('DjangoRequester')
            ->disableOriginalConstructor()
            ->disableOriginalClone()
            ->disableArgumentCloning()
            ->disallowMockingUnknownTypes()
            ->getMock();

        $response = $requesterStub->request("nonexistant/irrelevantQuery");
        $this->assertEquals('', $response);
    }
}
