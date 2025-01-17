import { getJSON } from "../../../../../../static/js/fetch.js";
import { appendAlert } from "../../../../../../static/js/alerts.js";

async function importBinance() {
  try {
    let response = await getJSON("/imports/from-binance");
    appendAlert(response.message, "success");
  } catch (error) {
    appendAlert(error.message, "danger");
  }
}

document.querySelector("#import").addEventListener("click", importBinance);
