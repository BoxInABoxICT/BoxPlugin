// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

var studenttime_block_chart = new PageLineChart("studenttime_block_chart");


/**
 * Setup visualisations of the data that was received.
 * 
 * @param {object} data The data from the dataloader
 * @returns {bool} True if there was enough data, false if not
 */
function studenttime_block_init(pageData) {
    if (pageData.graphs.length < 1) {
        return false;
    }

    //Get all the dates in the range of dates in the graphs
    var dateRange = getMinMaxDate(pageData.graphs, 1);
    var rangePoints = getAllDatesBetween(new Date(dateRange.min), new Date(dateRange.max));
    
    //Add the empty points to each graph, group by section, and then remove the doubles
    pageData.graphs = pageData.graphs.map(graph => studenttime_block_extendGraph(rangePoints, graph));
    pageData.graphs = groupOn(pageData.graphs, elem => elem.section, elem => elem, (total, elem) => {
      total.points = total.points.concat(elem.points);
      return total;
    });
    pageData.graphs = pageData.graphs.map(graph => studenttime_block_normalizeGraph(graph));

    //Update the chart data
    studenttime_block_chart.setData(
        pageData.graphs[0].points.map(point => getDateString(point.date)),
        pageData.graphs.map(graph => {
          return {
            label: graph.section_name,
            data: graph.points.map(point => Math.round(point.time/60))
          };
        })
    );

    return true;
}

/**
 * Add additional dates to a dataset.
 * 
 * @param {[{date: Date, count: number}]} allDataPoints The list of dates to append 
 * @param {[{time: number, date: (Date|string), count: number}]} graph The original dataset
 * @return {[{time: number, date: (Date|string), count: number}]} The extended graph
 */
function studenttime_block_extendGraph(allDataPoints, graph) {
  
    //Make sure both sets have the same format
    allDataPoints = allDataPoints.map(date => {
        return {
          'time': 0,
          'count': 0,
          'date': new Date(date)
        };
    });
    graph.points = graph.points.map(point => { 
      return {
        'time': parseInt(point.time),
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
 * @param {[{time: number, count: number, date: Date}]} graph.points The graph to normalize
 * @return {object} The original graph, but with normalized points
 */
function studenttime_block_normalizeGraph(graph) {

    //Group the points by date and add up the count and the time of all elements with the same date
    points = groupOn(graph.points, point => point.date, elem => elem, (total, point) => {
      total.count += point.count;
      total.time += point.time;
      return total;
    });

    //Change all dates into an actual date format
    points = points.map(point => {
      point.date = new Date(point.date);
      return point;
    });
  
    //Sort by date
    graph.points = points.sort((a,b) => a.date - b.date);

    return graph;
}
  