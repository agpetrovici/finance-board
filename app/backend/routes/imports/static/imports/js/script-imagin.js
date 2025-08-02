import { sendJSONgetJSON } from "../../../../../../static/js/fetch.js";
import { appendAlert } from "../../../../../../static/js/alerts.js";

async function importImagin() {
  const fileInput = document.querySelector("#file-input");

  if (!fileInput.files || fileInput.files.length === 0) {
    appendAlert("Please select a file", "warning");
    return;
  }

  const file = fileInput.files[0];

  try {
    // Read file as base64
    const base64Content = await readFileAsBase64(file);

    const data = {
      file: base64Content,
      filename: file.name,
    };

    const response = await sendJSONgetJSON("/imports/from-imagin", data);
    appendAlert(response.message, "success");
  } catch (error) {
    appendAlert(error.message, "danger");
  }
}

function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      // Remove the data URL prefix (e.g., "data:text/csv;base64,")
      const base64 = reader.result.split(",")[1];
      resolve(base64);
    };
    reader.onerror = () => reject(new Error("Failed to read file"));
    reader.readAsDataURL(file);
  });
}

document
  .querySelector("#imagin-import")
  .addEventListener("click", importImagin);
