import { categories, series } from "./test-data.js";

import { graphBarStacked } from "./graph-bar-stacked.js";

document.addEventListener("DOMContentLoaded", async function () {
  graphBarStacked(series, categories, "#column-chart-categories");
});
