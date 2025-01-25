export function graphBarStacked(
  series,
  categories,
  containerId,
  customColors = null
) {
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
      colors: customColors || [
        "#008FFB",
        "#00E396",
        "#FEB019",
        "#FF4560",
        "#775DD0",
        "#546E7A",
        "#26a69a",
        "#D10CE8",
      ],
      series: seriesData,
      tooltip: {
        custom: function ({ series, seriesIndex, dataPointIndex, w }) {
          const tooltips =
            w.config.series[seriesIndex].data[dataPointIndex].tooltip;
          return `<ul style="list-style-type: none; padding-left: 0; margin: 0;">
            ${tooltips.map((tip) => `<li>${tip}</li>`).join("")}
          </ul>`;
        },
      },
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
