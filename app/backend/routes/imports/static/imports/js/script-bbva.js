import { sendJSONgetJSON } from "../../../../../../static/js/fetch.js";
import { appendAlert } from "../../../../../../static/js/alerts.js";

async function importBBVA() {
  let text = document.querySelector("#bbva-data").value;
  let accountPk = document.querySelector("#account-pk").value;
  let data = { text: text, accountPk: accountPk };
  try {
    let response = await sendJSONgetJSON("/imports/from-bbva", data);
    appendAlert(response.message, "success");
  } catch (error) {
    appendAlert(error.message, "danger");
  }
}

document.querySelector("#bbva-import").addEventListener("click", importBBVA);

