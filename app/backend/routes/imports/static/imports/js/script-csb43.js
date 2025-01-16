import { appendAlert } from "../../../../../../static/js/alerts.js";
import { sendFilegetJSON } from "../../../../../../static/js/fetch.js";

async function importCsb43() {
  let dataElement = document.querySelector("#file-input");

  try {
    let response = await sendFilegetJSON(
      "/imports/from-norma43",
      "#file-input"
    );
    for (let message of response.messages) {
      appendAlert(message, "success");
    }
  } catch (error) {
    for (let message of response.messages) {
      appendAlert(message, "danger");
    }
  }
}

document.querySelector("#btn-import").addEventListener("click", importCsb43);
