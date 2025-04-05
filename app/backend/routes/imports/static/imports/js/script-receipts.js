import { appendAlert } from "../../../../../../static/js/alerts.js";

async function getReceiptData() {
  const fileInput = document.querySelector("#receipt-image");

  if (!fileInput.files || fileInput.files.length === 0) {
    appendAlert("Please select a receipt image first.", "danger");
    return;
  }

  const formData = new FormData();
  formData.append("receipt", fileInput.files[0]);

  try {
    const response = await fetch("/imports/get-receipt-data", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    appendAlert("Error processing receipt. Please try again.", "danger");
  }
}

function displayReceiptImage(data) {
  const receiptCanvas = document.querySelector("#receipt-canvas");

  if (data && data.data && data.data.image) {
    const ctx = receiptCanvas.getContext("2d");
    const img = new Image();
    img.onload = function () {
      // Clear the canvas
      ctx.clearRect(0, 0, receiptCanvas.width, receiptCanvas.height);

      // Calculate dimensions to maintain aspect ratio
      const scale = Math.min(
        receiptCanvas.width / img.width,
        receiptCanvas.height / img.height
      );

      const centerX = (receiptCanvas.width - img.width * scale) / 2;
      const centerY = (receiptCanvas.height - img.height * scale) / 2;

      // Draw the image on the canvas
      ctx.drawImage(
        img,
        centerX,
        centerY,
        img.width * scale,
        img.height * scale
      );
    };
    img.src = "data:image/jpeg;base64," + data.data.image;
  } else {
    console.error("No image data available");
  }
}

async function handleReceiptProcessing() {
  const data = await getReceiptData();
  displayReceiptImage(data);
}

document.addEventListener("DOMContentLoaded", () => {
  const processButton = document.querySelector("#btn-process-receipt");
  processButton.addEventListener("click", handleReceiptProcessing);
});
