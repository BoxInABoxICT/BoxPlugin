// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.


var dialoguetrainer_block_chart = new PageBoxPlot("dialoguetrainer_block_chart");


/**
 * Setup visualisations of the data that was received.
 * 
 * @param {object} data The data from the dataloader
 * @returns {bool} True if there was enough data, false if not
 */
function dialoguetrainer_block_init(data) {
    console.log(deepClone(data));
    if (data.scenarios.length < 1)
        return false;

    dialoguetrainer_block_chart.setData(
        data.scenarios.map(scen => "Scenario " + scen.id + "  {" + scen.count + "}"),
        [{'label': 'Best attempt statistics', 'data': data.scenarios.map(scen => dialoguetrainer_block_setToBoxplotData(scen))}]
    );

    
    return true;
}

/**
 * Extract the data from a set of data to a list that will translate into the correct boxplot.
 * @param {object} set The set containing min, q1, median, q3, max keys.
 * @returns {[number]}
 */
function dialoguetrainer_block_setToBoxplotData(set) {
    return [
        set.min,
        set.q1,
        set.median,
        set.q3,
        set.max
    ];
}