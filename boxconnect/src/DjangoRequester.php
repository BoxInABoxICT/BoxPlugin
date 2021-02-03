<?php

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

include 'HttpRequest.php';

//defined('MOODLE_INTERNAL') || die();

/**
 * Handles communication between moodle and the Django analytics app
 */
class DjangoRequester
{
    private $endpoint;
    private $token;
    private $request;

    /**
     * Constructs the DjangoRequester object.
     * @param string $url Allows for custom url to be secified
     */
    public function __construct(string $url = null)
    {
        if ($url == null) {
            $this->endpoint = get_config('local_boxconnect', 'endpoint');
            $this->token    = get_config('local_boxconnect', 'token');
        } else {
            $this->endpoint = $url;
        }
    }

    /**
     * Sends a Http request to the specified endpoint in the Django service.
     * @param string $pattern The url pattern for the desired function to call in Django service.
     *               Variable values should be embedded in the pattern
     * @param string $data JSON string if a POST request is required.
     *               Defaults to null when not set.
     * @return string response body of the Django service
     * @throws Exception if replycode is anything else than 200 OK
     */
    public function request(string $pattern, $data = null): string
    {
        return $this->requestCall($pattern, new CurlRequest($this->endpoint), $data);
    }

    /**
     * Method called by the request() method, with an additional argument facilitating testing
     * @param string $pattern The url pattern for the desired function to call in Django service.
     *               Variable values should be embedded in the pattern
     * @param string $data JSON data to be send with the request.
     *               When null, this generates a GET request, when populated it generates a POST request.
     * @return string response body of the Django service
     * @throws Exception if replycode is anything else than 200 OK
     */
    private function requestCall(string $pattern, HttpRequest $request, $data): string
    {
        $url = $this->endpoint . $pattern;
        $token = $this->token;
        $headers = array('Authorization: Token ' . $token, 'Content-Type:application/json');

        $request->SetOpt(CURLOPT_HTTPHEADER, $headers);
        $request->setOpt(CURLOPT_URL, $url);
        $request->setOpt(CURLOPT_RETURNTRANSFER, true);
        $request->setOpt(CURLOPT_FAILONERROR, true);

        if ($data != null) {
            $request->setOpt(CURLOPT_POST, true);
            $request->setOpt(CURLOPT_POSTFIELDS, $data);
        }

        $reply = $request->exec();
        $errorcode = $request->errNo();
        $error = $request->error();
        $request->close();
        if ($errorcode) {
            throw new Exception($error);
        }

        return $reply;
    }
}
