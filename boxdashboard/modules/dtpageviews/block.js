// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * Setup visualisations of the data that was received.
 * 
 * @param {object} data The data from the dataloader
 * @returns {bool} True if there was enough data, false if not
 */
function dtpageviews_block_init(data) {
    if (data.scenarios.length < 1)
        return false;
    
    data.scenarios = data.scenarios.map(scenario => {
        scenario.pageCoefs = scenario.pageCoefs.map(page => {
            if (page.coef > 2)
                page.coef = "<span class='text-success'>High</span>";
            else if (page.coef < -2)
                page.coef = "<span class='text-danger'>Low</span>";
            else
                page.coef = "<span class='text-secondary'>Average</span>";
            return page;
        });
        return scenario;
    });
     
    var template = document.getElementById('dtpageviews_block_template').innerHTML;
    var compiledTemplate = Template7.compile(template);
    var output = compiledTemplate({
        "scenarios": data.scenarios
    });
    
    document.getElementById('dtpageviews_block_accordion').innerHTML = output;

    return true;
}