// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

var participation_details_assignment_chart = new PageBarChart("participation_details_assignments_chart");
var participation_details_quizzes_chart = new PageBarChart("participation_details_quizzes_chart");

/**
 * Setup visualisations of the data that was received.
 * 
 * @param {object} data The data from the dataloader
 * @returns {bool} True if there was enough data, false if not
 */
function participation_details_init(data) {

    //Update the assignment completion chart
    participation_details_updateChart(
        participation_details_assignment_chart, 
        data.assignmentCompletion,  
        "Percentage of students that completed the assignment"
    );

    //Update the quiz completion chart
    participation_details_updateChart(
        participation_details_quizzes_chart, 
        data.quizCompletion,  
        "Percentage of students that completed the quiz"
    );

    //Update the list of pageview charts
    data.pageviews = Object.values(_.groupBy(data.pageviews, elem => elem.section));
    subcharts = participation_details_createSubCharts(data.pageviews.length);
    data.pageviews.map((set, index) => {
        subchart = subcharts[index];
        participation_details_updateChart(subchart, set, "Per page percentage for " + set[0].section_name);
    });


    return true;
}

/**
 * Update a chart with the (single) correct set of data.
 * 
 * @param {object} chart The PageChart to update
 * @param {[{section: number, module_name: string, percentage: number}]} newData 
 * @param {string} label The label to give to the dataset
 * @return {void}
 */
function participation_details_updateChart(chart, newData, label) {
    newData = newData.sort((a, b) => a.section - b.section);

    chart.setData(
        newData.map(mod => mod.module_name),
        [
            {
                label: label,
                data: newData.map(mod => mod.percentage * 100),
            }
        ]
    );
}

/**
 * Create a number of barcharts in the "#participation_details_perpagedistinct" element.
 * 
 * @param {number} count The amount of subcharts to create
 * @return {[object]} A list of PageBarChart with length {count}
 */
function participation_details_createSubCharts(count) {
    //Find the correct container and clear it
    containerID = "participation_details_perpagedistinct";
    charts = [];
    container = document.getElementById(containerID);
    container.innerHTML = "";
    
    //Create {count} charts in the container
    for (var i = 0; i<count; i++) {
        //Create a canvas element
        id = containerID + "_chart_" + i;
        chartelem = document.createElement("canvas");
        chartelem.id = id;

        //Add the canvas to the container
        if (i > 0)
          container.appendChild(document.createElement("hr"));
        container.appendChild(chartelem);

        //Create a chart from the canvas
        chart = new PageBarChart(id);
        charts.push(chart);
    }
    
    return charts;
  }