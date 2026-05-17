import { getJSON } from "../../../../../static/js/fetch.js";
import { graphBarStacked } from "./graph-bar-stacked.js";

const STOCK_CHART_COLORS = [
  "#00E396",
  "#008FFB",
  "#FEB019",
  "#775DD0",
  "#FF4560",
  "#546E7A",
  "#26a69a",
  "#D10CE8",
];

async function initStockChart() {
  const data = await getJSON("/api/get-stock-statement");
  graphBarStacked(
    data.series,
    data.categories,
    "#column-chart-stock",
    STOCK_CHART_COLORS,
    {
      xaxis: {
        type: "category",
        categories: data.categories,
        labels: {
          formatter: (value) => {
            const d = new Date(value);
            return d.toLocaleDateString("en-GB", { month: "short", year: "numeric" });
          },
        },
      },
      yaxis: {
        labels: {
          formatter: (value) => Math.round(value),
        },
      },
    }
  );
}

document.addEventListener("DOMContentLoaded", initStockChart);
