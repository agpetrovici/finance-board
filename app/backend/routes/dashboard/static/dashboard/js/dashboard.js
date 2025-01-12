import { getJSON } from "../../../../../static/js/fetch.js";
import { graph_line } from "./graph_line.js";

document.addEventListener("DOMContentLoaded", async function () {
  const data = await getJSON("/api/get-bank-statement");

  graph_line(data);
});
