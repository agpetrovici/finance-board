// import { categories, series } from "./test-data.js";
import { getJSON } from "../../../../../static/js/fetch.js";
import { graphBarStacked } from "./graph-bar-stacked.js";

document.addEventListener("DOMContentLoaded", async function () {
  const data = await getJSON("/api/test-get-transaction-by-day");
  let series = data.series;
  let categories = data.categories;
  graphBarStacked(series, categories, "#column-chart-categories");
});
