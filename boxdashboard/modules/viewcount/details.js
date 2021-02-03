// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

var viewcount_details_chart = new PageLineChart("viewcount_details_chart");


/**
 * Setup visualisations of the data that was received
 * 
 * @param {object} data The data from the dataloader
 * @returns {bool} True if there was enough data, false if not
 */
function viewcount_details_init(pageData) {
  if (pageData.graphs.length < 1)
    return false;

  document.getElementById("viewcount_details_totalcount").textContent = pageData.count;

  preprocessed = viewcount_details_preProcess(pageData.graphs);
  

  daygraphs = groupOn(deepClone(preprocessed), elem => elem.section, elem => elem, (total, elem) => {
    total.points = total.points.concat(elem.points);
    return total;
  });
  daygraphs = daygraphs.map(graph => viewcount_details_normalizeGraph(graph));

  viewcount_details_chart.setData(
    daygraphs[0].points.map(point => getDateString(point.date)),
    daygraphs.map(graph => {
      return {
        label: graph.section_name,
        data: graph.points.map(point => point.count)
      };
    })
  );
  
  subcharts = _.groupBy(preprocessed, 'section');
  sections = Object.keys(subcharts);
  viewcount_details_indvcharts = viewcount_details_createSubCharts(sections.length);
  sections.map((sectionID,index) => {
    subchart = subcharts[sectionID];
    chart = viewcount_details_indvcharts[index];
    chart.setData(
      subchart[0].points.map(point => getDateString(point.date)),
      subchart.map(graph => {
        return {
          label: graph.module_name,
          data: graph.points.map(point => point.count)
        };
      })
    );
    chart.setTitle(subchart[0].section_name);
  });

  return true;
}

/**
 * Create a number of barcharts in the "#participation_details_perpagedistinct" element.
 * 
 * @param {number} count The amount of subcharts to create
 * @return {[object]} A list of PageBarChart with length {count}
 */
function viewcount_details_createSubCharts(count) {
  charts = [];
  //Get the element and clear it
  containerID = "viewcount_details_subchartcontainer";
  container = document.getElementById(containerID);
  container.innerHTML = "";
  
  //Add {count} graphs to the element
  for (var i = 0; i<count; i++) {
      //Create the canvas
      id = containerID + "_chart_" + i;
      chartelem = document.createElement("canvas");
      chartelem.id = id;

      //Append the canvas to the container
      if (i > 0)
        container.appendChild(document.createElement("hr"));
      container.appendChild(chartelem);

      //Create the chart
      chart = new PageLineChart(id);
      charts.push(chart);
  }

  return charts;
}

/**
 * Preprocess all the graphs by making each graph have the same length and data domain.
 * 
 * @param {[object]} inGraphs The original graphs
 * @return {[object]} The pre-processed graphs
 */
function viewcount_details_preProcess(inGraphs) {
  graphs = deepClone(inGraphs);

  //Get all the dates in the entire timespan of the data in the graphs
  var dateRange = getMinMaxDate(graphs, 1);
  var rangePoints = getAllDatesBetween(dateRange.min, dateRange.max);

  //For each graph, add all the dates, and then remove the doubles
  graphs = graphs.map(graph => {
    graph = viewcount_details_expandGraph(rangePoints, graph);
    graph = viewcount_details_normalizeGraph(graph);
    return graph;
  });

  return graphs;
}

/**
 * Add additional dates to a dataset.
 * 
 * @param {[{date: Date, count: number}]} allDataPoints The list of dates to append 
 * @param {[{date: (Date|string), count: number}]} graph The original dataset
 * @return {[{date: (Date|string), count: number}]} The extended graph
 */
function viewcount_details_expandGraph(allDataPoints, graph) {

  //Make sure both sets have the same format
  graph.points = graph.points.map(point=> {
    return {'date': new Date(point.date), 'count': point.count};
  });
  allDataPoints = allDataPoints.map(date => {
    return {'date': new Date(date), 'count': 0};
  });

  //combine the sets
  graph.points = graph.points.concat(allDataPoints);

  return graph;
}

/**
 * Normalize the graph by removing double dates and aggregating those.
 * 
 * @param {object} graph The graph to normalize
 * @param {[{count: number, date: Date}]} graph.points The graph to normalize
 * @return {object} The original graph, but with normalized and sorted points
 */
function viewcount_details_normalizeGraph(graph) {
  //Apply a reduce/fold on the points
  points = groupOn(graph.points, elem => elem.date, elem => elem, (total, elem) => {
    total.count = total.count + elem.count;
    return total;
  });

  //Map the date of each point back to a date object and sort the points
  points = points.map(point => {
    point.date = new Date(point.date);
    return point;
  });
  graph.points = points.sort((a,b) => a.date - b.date);
  
  return graph;

}
