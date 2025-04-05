import { appendAlert } from "../../../../../../static/js/alerts.js";

const fileInput = document.querySelector("#receipt-image");
const receiptCanvas = document.querySelector("#receipt-canvas");

async function getReceiptData() {
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

async function displayReceiptImage() {
  if (!fileInput.files || fileInput.files.length === 0) {
    appendAlert("Please select a receipt image first.", "danger");
    return;
  }

  const file = fileInput.files[0];
  const fileURL = URL.createObjectURL(file);

  const ctx = receiptCanvas.getContext("2d");
  const img = new Image();

  // Convert the onload callback to a Promise
  return new Promise((resolve) => {
    img.onload = function () {
      ctx.clearRect(0, 0, receiptCanvas.width, receiptCanvas.height);

      const scale = Math.min(
        receiptCanvas.width / img.width,
        receiptCanvas.height / img.height
      );

      const centerX = (receiptCanvas.width - img.width * scale) / 2;
      const centerY = (receiptCanvas.height - img.height * scale) / 2;

      ctx.drawImage(
        img,
        centerX,
        centerY,
        img.width * scale,
        img.height * scale
      );

      // Store these values for later use
      receiptCanvas.currentScale = scale;
      receiptCanvas.currentCenterX = centerX;
      receiptCanvas.currentCenterY = centerY;

      URL.revokeObjectURL(fileURL);
      resolve();
    };

    img.src = fileURL;
  });
}

function displayBoundingBox(bbox) {
  if (!bbox || !Array.isArray(bbox) || bbox.length !== 4) {
    console.log("Invalid bbox:", bbox);
    return;
  }

  const ctx = receiptCanvas.getContext("2d");
  const scale = receiptCanvas.currentScale;
  const centerX = receiptCanvas.currentCenterX;
  const centerY = receiptCanvas.currentCenterY;

  // Get the original image dimensions from the file
  const img = new Image();
  img.src = URL.createObjectURL(fileInput.files[0]);

  img.onload = () => {
    // Calculate the rectangle coordinates in canvas space
    const x = centerX + bbox[0][0] * img.width * scale;
    const y = centerY + bbox[0][1] * img.height * scale;
    const width = (bbox[2][0] - bbox[0][0]) * img.width * scale;
    const height = (bbox[2][1] - bbox[0][1]) * img.height * scale;

    // console.log("Drawing rectangle at:", {
    //   x,
    //   y,
    //   width,
    //   height,
    //   scale,
    //   centerX,
    //   centerY,
    // });

    // Draw the rectangle
    ctx.beginPath();
    ctx.strokeStyle = "red";
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, width, height);

    URL.revokeObjectURL(img.src);
  };
}

async function displayReceiptData(data) {
  console.log(data);
  displayBoundingBox(data.data.transaction.time.bbox);
}

async function handleReceiptProcessing() {
  await displayReceiptImage();
  const data = await getReceiptData();
  await displayReceiptData(data);
}

document.addEventListener("DOMContentLoaded", () => {
  const processButton = document.querySelector("#btn-process-receipt");
  processButton.addEventListener("click", handleReceiptProcessing);
});
