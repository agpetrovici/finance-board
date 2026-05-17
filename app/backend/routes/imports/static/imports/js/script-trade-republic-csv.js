import { appendAlert } from "../../../../../../static/js/alerts.js";

async function importCsv() {
  const fileInput = document.querySelector("#csvFile");
  const accountPk = document.querySelector("#account-pk").value;
  const file = fileInput.files[0];

  if (!file) {
    appendAlert("Please select a CSV file.", "danger");
    return;
  }

  if (!accountPk) {
    appendAlert("Please select an account.", "danger");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("account_pk", accountPk);

  try {
    const response = await fetch("/imports/from-trade-republic-csv", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Network response was not ok.");
    }

    if (data.status === "success") {
      appendAlert(data.message, "success");
      fileInput.value = "";
    } else {
      appendAlert(data.message, "danger");
    }
  } catch (error) {
    appendAlert(`An error occurred: ${error.message}`, "danger");
  }
}

function handleImportClick() {
  importCsv();
}

document.querySelector("#stock-import").addEventListener("click", handleImportClick);
