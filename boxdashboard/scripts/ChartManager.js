// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.


/**
 * Create a list of dates between two dates, with exactly one date per week between and including the input dates.
 * 
 * @param {Date} date1 The lower bound date
 * @param {Date} date2 The upper bound date
 * @return {[Date]} A list of dates
 */
function getAllWeekDatesBetween(date1, date2) {
    var dateArray = [];
    var currentDate = new Date(date1.getTime());

    //Keep adding the date while it is smaller than the end date
    while (currentDate <= date2) {
        dateArray.push(new Date(currentDate.getTime()));
        currentDate.setDate(currentDate.getDate() + 7);
    }

    return dateArray;
}
  
/** 
 * Create a list of all dates between two dates.
 * 
 * @param {Date} date1 The lower bound date
 * @param {Date} date2 The upper bound date
 * @return {[Date]} A list of all the dates
*/
function getAllDatesBetween(date1, date2) {
    var dateArray = [];
    var currentDate = new Date(date1.getTime());

    //Keep adding the date while it is smaller than the end date
    while (currentDate <= date2) {
        dateArray.push(new Date(currentDate.getTime()));
        currentDate.setDate(currentDate.getDate() + 1);
    }

    return dateArray;
}

/**
 * Get the defauld linechart options.
 * 
 * @return {object} Default chart options
 */
function defaultLineChartOptions() {
    return {
        scales: {
            yAxes: [
                {
                    ticks: {
                        beginAtZero: true
                    }
                }
            ]
        }
    };
}

/**
 * Get the default barchart options.
 * 
 * @return {object} Default chart options
 */
function defaultBarChartOptions() {
    return {
        scales: {
            yAxes: [{
                barPercentage: 0.6,
                ticks: {
                    min: 0,
                    max: 100
                },
            }]
        }
    };
}


/**
 * Get the default boxplot options.
 * 
 * @return {object} Default chart options
 */
function defaultBoxPlotOptionsPositive() {
    return {
        scales: {
            yAxes: [{
                ticks: {
                    min: 0,
                    max: 100
                },
            }]
        }
    };
}

/**
 * Get the default boxplot options.
 * 
 * @return {object} Default chart options
 */
function defaultBoxPlotOptionsPosNeg() {
    return {
        scales: {
            yAxes: [{
                ticks: {
                    min: -100,
                    max: 100
                },
            }]
        }
    };
}


/**
 * An interface and representation for a chart on the dashboard
 * @abstract
 */
class PageChart {

    /**
     * PageChart constructor.
     * 
     * @param {string} element The id of the canvas element that the chart should be drawn on
     */
    constructor(element) {
        this.element = element;
        this.context = document.getElementById(element);
    }

    /**
     * Change the date displayed in the chart.
     * 
     * @param {[string]} labels The labels to be displayed on the x-axis
     * @param {[{label: string, data: [number]}]} plots A list of datasets of the same size, each containing a label and the values in the dataset
     * @return {void}
     */
    setData(labels, plots) {
        this.chart.data.labels = labels;
        this.chart.data.datasets = this.getDataLines(plots);
        this.chart.update();
    }

    /**
     * Change the title of the graph.
     * 
     * @param {(string|null)} title The title to be displayed or null to remove the title
     * @return {void}
     */
    setTitle(title) {
        this.chart.options.title = title != null ? {display: true, text: title} : {display: false, text: ""};
        this.chart.update();
    }
}

/**
 * An interface and representation for a line chart on the dashboard.
 */
class PageLineChart extends PageChart {

    /**
     * PageLineChart constructor.
     * 
     * @param {string} element The id of the canvas element that the chart should be drawn on
     */
    constructor(element) {
        super(element);
        this.chart = new Chart(this.context, {
            type: "line",
            data: {
                labels: [],
                datasets: []
            },
            options: defaultLineChartOptions()

        });
    
    }

    /**
     * Create the datasets from a set of data.
     * 
     * @param {[{label: string, data: [number]}]} plots A set of data to create datasets for
     * @return {[object]} A list of datasets
     */
    getDataLines(plots) {
        return plots.map(function(plot) {
            return {
                label: plot.label,
                data: plot.data,
                borderColor: randomColor(),
                borderWidth: 2,
                fill: false
            };
        });
    }
}

/**
 * An interface and representation for a bar chart on the dashboard.
 */
class PageBarChart extends PageChart {

    /**
     * PageBarChart constructor.
     * 
     * @param {string} element The id of the canvas element that the chart should be drawn on
     */
    constructor(element) {
        super(element);
        this.chart = new Chart(this.context, {
            type: "bar",
            data: {
                labels:[],
                datasets:[],
            },
            options: defaultBarChartOptions()
        });
    }

    /**
     * Create the datasets from a set of data.
     * 
     * @param {[{label: string, data: [number]}]} plots A set of data to create datasets for
     * @return {[object]} A list of datasets
     */
    getDataLines(plots) {
        return plots.map(function(plot) {
            return {
                label: plot.label,
                data: plot.data,
                backgroundColor: "#4dd168"
            };
        });
    }
}

/**
 * An interface and representation for a boxplot chart on the dashboard.
 */
class PageBoxPlot extends PageChart {

    /**
     * PageBoxPlot constructor.
     * 
     * @param {string} element The id of the canvas element that the chart should be drawn on
     */
    constructor(element) {
        super(element);
        this.chart = new Chart(this.context, {
            type: "boxplot",
            data: {
                labels:[],
                datasets:[],
            },
            options: defaultBoxPlotOptionsPositive()
        });
    }

    /**
     * Create the datasets from a set of data.
     * 
     * @param {[{label: string, data: [number]}]} plots A set of data to create datasets for
     * @return {[object]} A list of datasets
     */
    getDataLines(plots) {
        return plots.map(function(plot) {
            return {
                label: plot.label,
                data: plot.data,
                backgroundColor: "#fc0",
                borderColor: "black",
            };
        });
    }
}