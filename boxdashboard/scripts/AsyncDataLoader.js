// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.


// -------------------------------
// This script loads charts asynchronously based on generated links.
// -------------------------------

// Constants
var keyword = "chart"; // What keyword do we use to find data? Used in HTML like: data-<KEYWORD>-<ID>
var loadscriptURL = "dataloader.php";


// Waits for the document to be done with loading, then extends the page with the functions within.
$( document ).ready(function() {

    // When document is ready, automatically select the first tab selector and append active class to it
    const firstSelector = $('.load-request').first();
    initAsync(firstSelector, 'tab');
    firstSelector.addClass("active");
    $(firstSelector.attr("href")).addClass("active");

    // Function that listens to event click on DOM elements with class "load-request"
    $ ('.load-request').on('click', function(e) {
        initAsync($(this), 'tab');
    });
    $ ('.load-details-request').on('click', function(event) {
        initAsync($(this), 'modal');
    });

    // Inits the AsyncDataLoader
    function initAsync(localThis, viewtype) {
        

        // Extract all data from clicked DOM element with the keyword 
        var elementData = extractDataFromElement(localThis);
        var elementKeys = Object.keys(elementData);

        // If any alements are found
        if(elementKeys.length != 0){

            var url = constructURL(elementData,elementKeys);
            
            // Create an ajax call
            ajaxCall(url, viewtype, elementData);

        } else {
            console.error("Something went wrong, no attributes found!");
        }

    }

    // Extract data-tags from given element in an object
    function extractDataFromElement(element){

        var output = [];

        // Get all html "data-*" tags and values
        var allDataTags = element.data();
        
        // Get all keys from these properties (names)
        const dataProperties = Object.keys(allDataTags);

        // Loop through all keys and check if they relate to chart, then store them.
        dataProperties.forEach(property => {
            if(property.startsWith(keyword)){
                var propertyID = property.substr(keyword.length).toLowerCase();
                output[propertyID] = allDataTags[property];
            }
        });

        return output;
    }

    // Construct a HTTP GET URL
    function constructURL(data,keys){
        var query = loadscriptURL; // Start with basic load script and add parameters
        var countParameters = 0;

        keys.forEach(key => {
            countParameters += 1;
            // Hardcoded HTTP chars as the convention is that they will never change
            var httpChar = "?";

            // All other parameters other than the first should be seperated with "&"
            if(countParameters > 1) {
                httpChar = "&";
            }

            // Check if the data should be sent with the query. id's will never be sent.
            if(key != "id") {
                query += httpChar + key + "=" + data[key];
            }
        });

        return query;
    }

    // Make a jQuery AJAX call to the requested URL
    // Returns JSON with data
    function ajaxCall(url, viewtype, elementData){
        handleResult = function(result, viewtype) {
            if ("error" in result) {
                hideLoadingIcon(viewtype);
                displayError(result.error,viewtype);
            } else {
                hideLoadingIcon(viewtype);
                displayData(result,viewtype);

                if(viewtype == 'modal'){
                    showRefModal(elementData);
                }
            }
        };

        requestData = function() {
            try {
                showLoadingIcon(viewtype);
                $.ajax(
                    {   
                        // URL to send request to
                        url: url, 
                        // When succesful, drawgraph.
                        // This also includes backend errors
                        success: function(result){
                            handleResult(result, viewtype);
                        },
                        // Something with the request is wrong
                        error: function(jqXHR, textStatus, errorThrown){
                            hideLoadingIcon(viewtype);
                            displayError(errorThrown,viewtype);
                        },
                        // Maximum time for a request
                        timeout: 100000,
                        // Only accept JSON data
                        dataType: "json"
                    });
            }
            catch(exception){
                displayError(exception,viewtype);
            }
        };

        requestData();

        
    }

    // Shows the referenced modal
    function showRefModal(elementData){ 

        if($('#general-loading-modal').css('display') == 'none') {
            $('#general-loading-modal').modal('toggle');
        } else {
            $('#general-loading-modal').modal('hide');
        }
        
        $(elementData.targetactual).modal('show');
    }

    // Handles showing the loading icon
    function showLoadingIcon(viewtype){

        if(viewtype == 'tab'){
            $(".chart-loader-overlay").show();
        }
        
    }

    // Handles hiding the loading icon
    function hideLoadingIcon(viewtype){

        if(viewtype == 'tab'){
            $(".chart-loader-overlay").hide();
        }

    }

    // Display a general error
    function displayError(message,viewtype){

        if(viewtype == 'modal'){
            $('.modal').modal('hide');
            $('#general-error-modal').modal('show');
        } else {
            activaTab("boxdashboard-body-error-generic");
            console.log("An error occured: " + message);
        }
    }

    // Display a not enough info error
    function displayNei(){
        activaTab("boxdashboard-body-nei-generic");
    }

    // Activate a certain tab
    function activaTab(tab){
        $('.nav-tabs-chart-selector a[href="#' + tab + '"]').tab('show');
    }
    
    // Draw the graph with the data from async request
    function displayData(data,viewtype){
        // Check if init function exists in data from call
        if (data.initFunc != ""){ 
            var init = window[data.initFunc];
            if(typeof init === 'function') {
                // Draw the graph or display "not enough info" tabpane
                if(!init(data)) {
                    displayNei();
                }
            }
        }
        hideLoadingIcon(viewtype);
        
    }
});
