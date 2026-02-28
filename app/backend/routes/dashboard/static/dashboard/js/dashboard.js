import { getJSON } from "../../../../../static/js/fetch.js";
import { graphLine } from "./graph-line.js";

document.addEventListener("DOMContentLoaded", initFinanceChart);

async function initFinanceChart() {
  const data = await getJSON("/api/get-financial-series");
  graphLine(data.series);
}
