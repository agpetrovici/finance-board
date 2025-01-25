import { getJSON } from "../../../../../static/js/fetch.js";
import { graphLine } from "./graph-line.js";

document.addEventListener("DOMContentLoaded", async function () {
  const data = await getJSON("/api/get-bank-statement");

  graphLine(data);
});
