// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

var viewcount_block_chart = new PageLineChart("viewcount_block_chart");


/**
 * Setup visualisations of the data that was received
 * 
 * @param {object} data The data from the dataloader
 * @returns {bool} True if there was enough data, false if not
 */
function viewcount_block_init(pageData) {
  if (pageData.graphs.length < 1)
    return false;

  //Get all the weeks in the range of dates in the graphs
  var dateRange = getMinMaxDate(pageData.graphs, 8);
  var rangePoints = getAllWeekDatesBetween(new Date(dateRange.min), new Date(dateRange.max));
  
  //Add the empty points to each graph, group by section, and then remove the doubles
  pageData.graphs = pageData.graphs.map(graph => viewcount_block_extendGraph(rangePoints, graph));
  pageData.graphs = groupOn(pageData.graphs, elem => elem.section, elem => elem, (total, elem) => {
    total.points = total.points.concat(elem.points);
    return total;
  });
  pageData.graphs = pageData.graphs.map(graph => viewcount_block_normalizeGraph(graph));

  //Update the chart data
  viewcount_block_chart.setData(
    pageData.graphs[0].points.map(point => getWeekString(point.date)),
    pageData.graphs.map(graph => {
      return {
        label: graph.section_name,
        data: graph.points.map(point => point.count)
      };
    })
  );

  return true;
}

/**
 * Add additional dates to a dataset
 * 
 * @param {[{date: Date, count: number}]} allDataPoints The list of dates to append 
 * @param {[{date: (Date|string), count: number}]} graph The original dataset
 * @return {[{date: (Date|string), count: number}]} The extended graph
 */
function viewcount_block_extendGraph(allDataPoints, graph) {

  //Make sure both sets have the same format
  allDataPoints = allDataPoints.map(date => {
    return {'date': date, 'count': 0};
  });
  graph.points = graph.points.map(point => { 
    return {
      'count': point.count, 
      'date': new Date(point.date)
    };
  });

  //Combine the sets
  graph.points = graph.points.concat(allDataPoints);

  return graph;
}

/**
 * Normalize the graph by removing double dates and aggregating those.
 * 
 * @param {object} graph The graph to normalize
 * @param {[{count: number, date: Date}]} graph.points The graph to normalize
 * @return {object} The original graph, but with normalized points
 */
function viewcount_block_normalizeGraph(graph) {
  
  var points = graph.points;

  //Group the points by week and add up the point counts
  reducedPoints = points.reduce(function(total, point) {
    var date = new Date(point.date);
    var weekString =  getWeekString(date);
    if (weekString in total) {
      total[weekString].count += point.count;
    } else {
      total[weekString] = {'count': point.count, 'date': date};
    }
    return total;
  }, {} );

  //Turn the object back into an array
  points = Object.keys(reducedPoints).map(key => {
    return {'date': reducedPoints[key].date, 'count': reducedPoints[key].count};
  });

  //Sort by date
  points = points.sort((a,b) => a.date - b.date);
  
  graph.points = points;
  return graph;

}


