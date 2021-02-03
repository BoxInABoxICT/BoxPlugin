<?php
// phpcs:ignoreFile
// this file is a formatting mess,
// it is used for quick validation of php code and should NOT be present in the finished product

// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

// Standard config file and local library.

?>
<!DOCTYPE html>
<html>
<body>

<?php
use boxconnect;

require_once(__DIR__ . '/../../config.php');

// Setting up the page.
$PAGE->set_context(context_system::instance());
$PAGE->set_pagelayout('standard');
$PAGE->set_heading("Current LRS data");
$PAGE->set_url(new moodle_url('/local/boxconnect/index.php'));

// Ouput the page header.
echo $OUTPUT->header();

// section below is temporary
// for a more 'interactive' demo

?>
<h2> Some example queries:</h2>
<h5> statements? agent={"account":%20{"name":%20"2","homePage":%20"http://127.0.0.1:8080"}} </h5>
<h5> statements? statementId=5f608f7c-aa00-4d45-9381-e405ff012f32 </h5>
<h5> agents? agent={"account":%20{"homePage":%20"http://127.0.0.1:8080","name":%20"2"}} </h5>



<form action="http://localhost/local/boxconnect/index.php" method="post">
    <input type="text" name="query" >
    <input type="submit" name="submit" value="Submit">
</form>
</html>

<?php

/**
 * Handles communication between moodle and the Django analytics app
 */

include 'src/DjangoRequester.php';
$req = new DjangoRequester();

/**
* Sends a Http request with the entered @$queryparams to the specified endpoint in the Django service.
*/
$queryparams = $_POST['query'];
if (isset($_POST['submit'])) {
    $reply = $req->request($queryparams);
    echo $reply;
}

// Output the page footer.
echo $OUTPUT->footer();