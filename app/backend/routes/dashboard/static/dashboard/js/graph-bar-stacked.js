export function graphBarStacked(series, categories, containerId) {
  // Create container for all charts
  const chartsContainer = document.querySelector(containerId);
  const charts = [];

  // Generate charts dynamically
  series.forEach((seriesData, index) => {
    // Create div for this chart
    const chartDiv = document.createElement("div");
    chartDiv.id = `stacked-column${index + 1}`;
    chartsContainer.appendChild(chartDiv);

    // Generate options for this chart
    const options = {
      chart: {
        id: `chart${index + 1}`,
        type: "bar",
        height: 300,
        stacked: true,
        zoom: {
          enabled: true,
        },
        events: {
          zoomed: (chartContext, { xaxis }) => {
            // Update all other charts except this one
            charts.forEach((chart, i) => {
              if (i !== index) {
                chart.updateOptions({
                  xaxis: {
                    min: xaxis.min,
                    max: xaxis.max,
                  },
                });
              }
            });
          },
          scrolled: (chartContext, { xaxis }) => {
            // Update all other charts except this one
            charts.forEach((chart, i) => {
              if (i !== index) {
                chart.updateOptions({
                  xaxis: {
                    min: xaxis.min,
                    max: xaxis.max,
                  },
                });
              }
            });
          },
        },
      },
      series: seriesData,
      xaxis: {
        type: "datetime",
        categories: categories,
      },
    };

    // Create and render the chart
    const chart = new ApexCharts(chartDiv, options);
    charts.push(chart);
    chart.render();
  });
}