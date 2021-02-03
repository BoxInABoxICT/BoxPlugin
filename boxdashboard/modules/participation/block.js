// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course.
// ©Copyright Utrecht University Department of Information and Computing Sciences.

var participation_block_chart = new PageBarChart("participation_block_chart");


/**
 * Setup visualisations of the data that was received.
 * 
 * @param {object} data The data from the dataloader
 * @returns {bool} True if there was enough data, false if not
 */
function participation_block_init(data) {
    if (data.pageviews.length < 1)
        return false;

    //Group the pageviews by section
    data.pageviews = _.groupBy(data.pageviews, elem => elem.section);

    //For each section, calculate the average view percentage
    data.pageviews = Object.values(data.pageviews).map(set => {
        sum = set.map(elem => elem.percentage).reduce((acc, current) => acc + current);
        avg = sum / set.length;
        name = set[0].section_name;

        return {
            "section_name": name,
            "percentage": avg
        };
    });

    //Update the chart with the new data
    participation_block_chart.setData(
        data.pageviews.map(page => page.section_name),
        [
            {
                label: "Average percentage of students that viewed the page per topic",
                data: data.pageviews.map(page=> page.percentage * 100),
            }
        ]
    );
    
    return true;
}