import { appendAlert } from "../../../../../../static/js/alerts.js";

async function importStock() {
  const fileInput = document.querySelector("#pdfFiles");
  const files = fileInput.files;

  if (!files || files.length === 0) {
    appendAlert("Please select at least one PDF file.", "danger");
    return;
  }

  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]);
  }

  try {
    const response = await fetch("/imports/from-trade-republic", {
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
  importStock();
}

document.querySelector("#stock-import").addEventListener("click", handleImportClick);
