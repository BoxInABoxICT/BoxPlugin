// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.


/**
 * Setup visualisations of the data that was received.
 * 
 * @param {object} data The data from the dataloader
 * @returns {bool} True if there was enough data, false if not
 */
function dialoguetrainer_details_init(data) {

    console.log(deepClone(data));

    var template = document.getElementById('dialoguetrainer_details_template').innerHTML;
    var compiledTemplate = Template7.compile(template);
    var output = compiledTemplate({
        "scenarios": Object.keys(data.scenarios)
    });
    document.getElementById('dialoguetrainer_details_accordion').innerHTML = output;

    dialoguetrainer_details_setupCharts(data.scenarios);
  
    return true;
}


/**
 * Create charts in the empty canvases and display the correct data in them
 * 
 * @param {object} scenarios An object containing the betweenAttempts and betweenStudents data
 * @returns {null}
 */
function dialoguetrainer_details_setupCharts(scenarios) {
    Object.keys(scenarios).map((key) => {
        var chart1 = new PageBoxPlot("dialoguetrainer_details_" + key + "_chart1");
        var chart2 = new PageBoxPlot("dialoguetrainer_details_" + key + "_chart2");
        chart2.chart.options = defaultBoxPlotOptionsPosNeg();
        
        var betweenAttempts = scenarios[key].betweenAttempts.map(dialoguetrainer_details_setToBoxplotData);
        var betweenStudents = scenarios[key].betweenStudents.map(dialoguetrainer_details_setToBoxplotData);

        chart1.setData(
            betweenStudents.map((_item, index) => "attempt " + (index+1) + "  {" + scenarios[key].betweenStudents[index].count + "}"),
            [{"label": "Score per attempt in scenario " + key, "data": betweenStudents}]
        );

        chart2.setData(
            betweenAttempts.map((_item, index) => "attempt " + (index+1) + " >> " + (index+2)),
            [{"label": "Difference between attempts in scenario " + key, "data": betweenAttempts}]
        );
    });
}

/**
 * Extract the data from a set of data to a list that will translate into the correct boxplot.
 * @param {object} set The set containing min, q1, median, q3, max keys.
 * @returns {[number]}
 */
function dialoguetrainer_details_setToBoxplotData(set) {
    return [
        set.min,
        set.q1,
        set.median,
        set.q3,
        set.max
    ];
}