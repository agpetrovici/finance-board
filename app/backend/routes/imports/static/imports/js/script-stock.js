import { sendJSONgetJSON } from "../../../../../../static/js/fetch.js";
import { appendAlert } from "../../../../../../static/js/alerts.js";

async function importStock() {
  const stockData = document.querySelector("#stockData").value;
  const accountPk = document.querySelector("#account-pk").value;
  console.log(stockData);

  try {
    const data = await sendJSONgetJSON("/imports/from-stock", {
      text: stockData,
      accountPk: accountPk,
    });

    if (data.status === "success") {
      appendAlert(data.message, "success");
      document.querySelector("#stockData").value = "";
    } else {
      appendAlert(data.message, "danger");
    }
  } catch (error) {
    appendAlert(`An error occurred: ${error.message}`, "danger");
  }
}

document.querySelector("#stock-import").addEventListener("click", importStock);
