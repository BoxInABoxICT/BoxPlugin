// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.


// -------------------------------
// This script loads mofa settings and is able to edit them
// -------------------------------


// Waits for the document to be done with loading, then extends the page with the functions within.
$( document ).ready(function() {


    // Create some global constants
    const global_cid = getAllUrlParams().cid;
    const global_url = 'settingloader.php?cid=' + global_cid;
    const fetch = 'fetch';
    const update = 'update';
    
    // Init fetch on page load
    settingAjaxCall(global_url,fetch);

    // The render function
    // Uses template7 javascript library to render HTML from json through a template, displaying a form row for each object in JSON data.
    function renderSettingsHTML(json){

        // Use the template from dashboard HTML
        var template = $('#settings-template').html();

        var compiledTemplate = Template7.compile(template);
        var outputHTML = compiledTemplate(json);

        $("#settings-loadon").html(outputHTML);

    }

    // This function makes the POST request to the moodle backend
    function settingAjaxCall(url, type, data=null){

        if(type == 'fetch') {
            // If the settings are fetched from the specified endpoint on page load
            try {
                $.ajax(
                    {   
                        // URL to send request to
                        url: url, 
                        // Use GET on fetch
                        method: 'GET',
                        // When succesful, render HTML.
                        // This also includes backend errors
                        success: function(result){
                            renderSettingsHTML(result);
                            initSettingToggle();
                        },
                        // Something with the request is wrong
                        error: function(jqXHR, textStatus, errorThrown){
                            console.error("Error during settings load: " + errorThrown);
                        },
                        // Maximum time for a request
                        timeout: 10000,
                        // Only accept JSON data
                        dataType: "json"
                    });
            }
            catch(exception){
                console.error("Error during settings load");
            }
        }
        else if (type == 'update'){
            // When the user submits an update to the settingloader
            try {
                $.ajax(
                    {   
                        // URL to send request to
                        url: url, 
                        // Use POST on update
                        method: 'POST',
                        data: JSON.stringify(data),
                        contentType: 'application/json',
                        // When succesful, render HTML.
                        // This also includes backend errors
                        success: function(result){
                            renderSettingsHTML(result);
                            initSettingToggle();
                            $('#unapplied-changes').hide();
                        },
                        // Something with the request is wrong
                        error: function(jqXHR, textStatus, errorThrown){
                            console.error("Error during settings load" + errorThrown);
                        },
                        // Maximum time for a request
                        timeout: 10000,
                        // Only accept JSON data
                        dataType: "json"
                    });
            }
            catch(exception){
                console.error("Error during settings load");
            }
        }
        
    }



    // SUPPORT FUNCTIONS:

    // On form submit function
    $("#settings-apply-form").on('submit',function(e){
        e.preventDefault();

        // Serialize data from the HTML form
        var formdata = $(this).serializeArray();
        var courseid = $("#settings-apply-form-id").val();
        
        // Append the unchecked checkboxes to this data
        formdata = formdata.concat(
            $("#settings-apply-form input[type=checkbox]:not(:checked)").map(
                function(){
                    return {"name": this.name, "value": "false"};
                }
            ).get()
        );
        
        settingAjaxCall(global_url,update,formdata);

    });

    // Functions to make the dashboard feel more interactive by responding to user actions.
    function initSettingToggle(){
        $(".setting-toggle").on('change',function(){
            
            var targetID = $(this).data().target;
            
            var target = $(targetID);

            // Toggle the readonly property of target field when pressed
            $(target).prop('hidden', function(i, v) { return !v; });
        });
    }

    // Show unapplied changes
    $("#settings-apply-form").on("change keyup", function(){
        $('#unapplied-changes').show();
    });


    // Function to extract GET params from the current URL with legacy browser support
    // This function was pulled from https://www.sitepoint.com/get-url-parameters-with-javascript/
    // Authors: Yaphi Berhanu, James Hibbard
    // January 13, 2020

    // Returns an object with all GET parameter keys appointed to their value.
    // May be given a custom URL string parameter
    function getAllUrlParams(url) {

        // get query string from url (optional) or window
        var queryString = url ? url.split('?')[1] : window.location.search.slice(1);
      
        // we'll store the parameters here
        var obj = {};
      
        // if query string exists
        if (queryString) {
      
          // stuff after # is not part of query string, so get rid of it
          queryString = queryString.split('#')[0];
      
          // split our query string into its component parts
          var arr = queryString.split('&');
      
          for (var i = 0; i < arr.length; i++) {
            // separate the keys and the values
            var a = arr[i].split('=');
      
            // set parameter name and value (use 'true' if empty)
            var paramName = a[0];
            var paramValue = typeof (a[1]) === 'undefined' ? true : a[1];
      
            // (optional) keep case consistent
            paramName = paramName.toLowerCase();
            if (typeof paramValue === 'string') paramValue = paramValue.toLowerCase();
      
            // if the paramName ends with square brackets, e.g. colors[] or colors[2]
            if (paramName.match(/\[(\d+)?\]$/)) {
      
              // create key if it doesn't exist
              var key = paramName.replace(/\[(\d+)?\]/, '');
              if (!obj[key]) obj[key] = [];
      
              // if it's an indexed array e.g. colors[2]
              if (paramName.match(/\[\d+\]$/)) {
                // get the index value and add the entry at the appropriate position
                var index = /\[(\d+)\]/.exec(paramName)[1];
                obj[key][index] = paramValue;
              } else {
                // otherwise add the value to the end of the array
                obj[key].push(paramValue);
              }
            } else {
              // we're dealing with a string
              if (!obj[paramName]) {
                // if it doesn't exist, create property
                obj[paramName] = paramValue;
              } else if (obj[paramName] && typeof obj[paramName] === 'string'){
                // if property does exist and it's a string, convert it to an array
                obj[paramName] = [obj[paramName]];
                obj[paramName].push(paramValue);
              } else {
                // otherwise add the property
                obj[paramName].push(paramValue);
              }
            }
          }
        }
      
        return obj;
      }


});