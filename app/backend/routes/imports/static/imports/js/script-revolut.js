import { sendJSONgetJSON } from "../../../../../../static/js/fetch.js";
import { appendAlert } from "../../../../../../static/js/alerts.js";

async function importRevolut() {
  let text = document.querySelector("#revolut-data").value;
  let accountPk = document.querySelector("#account-pk").value;
  let data = { text: text, accountPk: accountPk };
  try {
    let response = await sendJSONgetJSON("/imports/from-revolut", data);
    appendAlert(response.message, "success");
  } catch (error) {
    appendAlert(error.message, "danger");
  }
}

document
  .querySelector("#revolut-import")
  .addEventListener("click", importRevolut);
