// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

/**
 * This file contains utility functions that are used troughout the dashboard. 
 */

/**
 * Get the weeknumber of the week a certain date is in.
 * 
 * @param {Date} dt The DateTime object to get the week of.
 * @return {number} A number between 1 and 53 
 */
function ISO8601_week_no(dt) 
{
    var tdt = new Date(dt.valueOf());
    var dayn = (dt.getDay() + 6) % 7;
    tdt.setDate(tdt.getDate() - dayn + 3);
    var firstThursday = tdt.valueOf();
    tdt.setMonth(0, 1);
    if (tdt.getDay() !== 4) 
      tdt.setMonth(0, 1 + ((4 - tdt.getDay()) + 7) % 7);
    return 1 + Math.ceil((firstThursday - tdt) / 604800000);
}

/**
 * Get the highest and lowest date from a set of graphs
 * 
 * @param {[{points: [{date: Date}]}]} graphs The set of graphs to get the highest and lowest date from
 * @param {number} margin The amount of days to expand the date ranges
 * @return {{min: Date, max: Date}} The minimum and maximum date
 */
function getMinMaxDate(graphs, margin = 0) {
  //Get the min and max date from each graph in the graph set
  localMinMax = graphs.map(graph => {
    var dates = graph.points.map(point => new Date(point.date));
    var min = Math.min(...dates);
    var max = Math.max(...dates);
    return {'min': min, 'max': max};
  });

  //Get the min and max date from the local min max values
  var minDates = localMinMax.map(dates=> dates.min);
  var maxDates = localMinMax.map(dates=> dates.max);
  var min = new Date(Math.min(...minDates));
  var max = new Date(Math.max(...maxDates));

  //Add the margin to the results
  min.setDate(min.getDate() - margin);
  max.setDate(max.getDate() + margin);
  return {'min': new Date(min), 'max': new Date(max) };
}

/**
 * Generates a random color.
 * 
 * @return {string} A string in the format of 'rgba({r},{g},{b},1)'
 */
function randomColor() {
  var r = Math.floor(Math.random() * 255);
  var g = Math.floor(Math.random() * 255);
  var b = Math.floor(Math.random() * 255);
  return "rgba(" + r + "," + g + "," + b + ",1)";
}

/**
 * Creates a string representation of a date.
 * 
 * @param {Date} date The date to get a string of
 * @return {string} The date in the format of 'dd-mm-yyyy'
 */
function getDateString(date) {
  date = new Date(date);
  return String(date.getDate()) + "-" + String(date.getMonth() + 1)  + "-" + String(date.getFullYear());
}

/**
 * Creates a string representation of the week a date is in.
 * 
 * @param {Date} date The date to get a string of
 * @return {string} The weekstring in the format of '{yyyy} week {weeknum}'
 */
function getWeekString(date) {
  date = new Date(date);
  week = ISO8601_week_no(date);
  return String(date.getFullYear()) +  " week " + week;
}

/**
 * Group an array on a specific key.
 * 
 * @param {[any]} data The array of data to be grouped
 * @param {function(any):(string|number)} keyFunc A function to extract a key from an element in the data array
 * @param {function(any):any} initFunc A function to create an initial value if the key does not exist yet
 * @param {function(any, any):any} grouping An aggregation function that combines the accumulated result and a new element into a new accumulated result.
 * @return {[any]} A copy of the result of the grouping
 */
function groupOn(data, keyFunc, initFunc, grouping) {
  newData = data.reduce(function(newset, elem) {
    ident = keyFunc(elem);
    if (ident in newset) {
      newset[ident] = grouping(newset[ident], elem);
    } else {
      newset[ident] = initFunc(elem);
    }
    return newset;
  }, {} );
  return deepClone(Object.values(newData));
}

/**
 * Deepclones an object by converting to a string and back.
 * 
 * @param {any} obj The object to clone
 * @return {any} A deep copy of the object
 */
function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}


