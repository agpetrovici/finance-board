import { appendAlert } from "../../../../../../static/js/alerts.js";
import { sendJSONgetJSON } from "../../../../../../static/js/fetch.js";
import { handleCameraUsage } from "./script-receipts-camera.js";

const fileInput = document.querySelector("#receipt-image");
const receiptCanvas = document.querySelector("#receipt-canvas");
const processButton = document.querySelector("#btn-process-receipt");
const cameraButton = document.querySelector("#btn-use-camera");

export async function getReceiptData() {
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

export async function displayReceiptImage() {
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

function createRectangle(bbox) {
  if (!bbox || !Array.isArray(bbox) || bbox.length !== 4) {
    console.log("Invalid bbox:", bbox);
    return null;
  }

  const scale = receiptCanvas.currentScale;
  const centerX = receiptCanvas.currentCenterX;
  const centerY = receiptCanvas.currentCenterY;

  // Get the original image dimensions from the file
  const img = new Image();
  img.src = URL.createObjectURL(fileInput.files[0]);

  return new Promise((resolve) => {
    img.addEventListener("load", function () {
      // Calculate the rectangle coordinates in canvas space
      const x = centerX + bbox[0][0] * img.width * scale;
      const y = centerY + bbox[0][1] * img.height * scale;
      const width = (bbox[2][0] - bbox[0][0]) * img.width * scale;
      const height = (bbox[2][1] - bbox[0][1]) * img.height * scale;

      // Create and return a rectangle object
      const rectangle = {
        x,
        y,
        width,
        height,
        color: "red",
        lineWidth: 2,
        fill: "rgba(0, 0, 0, 0)",
        draw(ctx) {
          ctx.beginPath();
          ctx.strokeStyle = this.color;
          ctx.lineWidth = this.lineWidth;
          ctx.strokeRect(this.x, this.y, this.width, this.height);
        },
        update(dx, dy) {
          this.x += dx;
          this.y += dy;
        },
      };

      // Draw the rectangle immediately
      const ctx = receiptCanvas.getContext("2d");
      rectangle.draw(ctx);

      URL.revokeObjectURL(img.src);
      resolve(rectangle);
    });
  });
}

function setRectangleFill(rectangle) {
  const ctx = receiptCanvas.getContext("2d");
  // Save the current state
  ctx.save();

  // Set fill style
  ctx.fillStyle = "rgba(255, 0, 0, 0.2)";

  // Fill the rectangle
  ctx.fillRect(rectangle.x, rectangle.y, rectangle.width, rectangle.height);

  // Restore the context to previous state
  ctx.restore();

  rectangle.draw(ctx);
}

function removeRectangleFill(rectangle) {
  const ctx = receiptCanvas.getContext("2d");

  // Only clear the specific rectangle area
  ctx.clearRect(rectangle.x, rectangle.y, rectangle.width, rectangle.height);

  // Redraw just that portion of the receipt image
  const img = new Image();
  img.src = URL.createObjectURL(fileInput.files[0]);

  img.onload = function () {
    // Calculate the source coordinates in the original image
    const sourceX =
      (rectangle.x - receiptCanvas.currentCenterX) / receiptCanvas.currentScale;
    const sourceY =
      (rectangle.y - receiptCanvas.currentCenterY) / receiptCanvas.currentScale;
    const sourceWidth = rectangle.width / receiptCanvas.currentScale;
    const sourceHeight = rectangle.height / receiptCanvas.currentScale;

    // Draw just the portion of the image that corresponds to this rectangle
    ctx.drawImage(
      img,
      sourceX,
      sourceY,
      sourceWidth,
      sourceHeight,
      rectangle.x,
      rectangle.y,
      rectangle.width,
      rectangle.height
    );

    // Add semi-transparent grey fill
    ctx.fillStyle = "rgba(128, 128, 128, 0)";
    ctx.fillRect(rectangle.x, rectangle.y, rectangle.width, rectangle.height);

    // Redraw the outline of the rectangle
    rectangle.draw(ctx);

    URL.revokeObjectURL(img.src);
  };
}

async function displayValue(data, variable_name) {
  // Get the value from the data
  const valueElement = document.querySelector(`#receipt-${variable_name}`);
  const imgElement = document.querySelector(`#receipt-${variable_name}-img`);

  valueElement.value = data.value;
  // Check if we have valid bbox data
  if (isValidBbox(data.bbox)) {
    let foundRectangle = await createRectangle(data.bbox);
    processReceiptCrop(data.bbox, imgElement);

    // Add event listener to highlight the rectangle when the input field is focused
    valueElement.addEventListener("focus", function () {
      setRectangleFill(foundRectangle);
    });
    valueElement.addEventListener("blur", function () {
      removeRectangleFill(foundRectangle);
    });
  } else {
    // Hide the image if no valid bbox
    imgElement.style.display = "none";
  }
}

function isValidBbox(bbox) {
  return bbox && Array.isArray(bbox) && bbox.length === 4;
}

function processReceiptCrop(bbox, valueElement) {
  // Get the original image from file input
  const originalImage = new Image();
  originalImage.src = URL.createObjectURL(fileInput.files[0]);

  originalImage.addEventListener("load", function () {
    const cropCoordinates = calculateCropCoordinates(bbox, originalImage);
    const croppedImage = cropImage(originalImage, cropCoordinates);

    // Set the cropped image as the source for the value element
    valueElement.src = croppedImage;
    valueElement.style.display = "block";

    // Clean up
    URL.revokeObjectURL(originalImage.src);
  });
}

function calculateCropCoordinates(bbox, originalImage) {
  return {
    x: bbox[0][0] * originalImage.width,
    y: bbox[0][1] * originalImage.height,
    width: (bbox[2][0] - bbox[0][0]) * originalImage.width,
    height: (bbox[2][1] - bbox[0][1]) * originalImage.height,
  };
}

function cropImage(originalImage, coords) {
  // Create a temporary canvas for cropping
  const tempCanvas = document.createElement("canvas");
  tempCanvas.width = coords.width;
  tempCanvas.height = coords.height;
  const tempCtx = tempCanvas.getContext("2d");

  // Draw the cropped portion to the temporary canvas
  tempCtx.drawImage(
    originalImage,
    coords.x,
    coords.y,
    coords.width,
    coords.height,
    0,
    0,
    coords.width,
    coords.height
  );

  return tempCanvas.toDataURL();
}

async function processList(data, variable_name) {
  const lineItemsContainer = document.querySelector(
    `#receipt-data-list-${variable_name}`
  );
  lineItemsContainer.innerHTML = "";

  data.data.transaction.line_items.forEach((item, index) => {
    const lineItem = document.createElement("div");
    lineItem.innerHTML = `
    <div class="mb-3 data-container" data-variable-name="${index}">
        <div class="input-group">
            <input type="text" class="form-control" id="receipt-${index}" value="${item.value}">
            <div class="input-group-append">
                <img class="img-fluid img-thumbnail" id="receipt-${index}-img" alt="image">
            </div>
        </div>
    </div>
    `;
    lineItemsContainer.appendChild(lineItem);
    displayValue(item, index);
  });
}

async function displayReceiptData(data) {
  const receiptDataContainers = document.querySelectorAll(
    "#receipt-data-container .data-container"
  );

  receiptDataContainers.forEach((container) => {
    const variableName = container.getAttribute("data-variable-name");
    if (container.classList.contains("individual")) {
      displayValue(data.data.transaction[variableName], variableName);
    } else {
      processList(data, variableName);
    }
  });
}

async function handleReceiptProcessing() {
  // Trigger file selection dialog
  fileInput.click();
}

// Function to handle file selection
async function handleFileSelection() {
  if (!fileInput.files || fileInput.files.length === 0) {
    return;
  }

  // Process the selected file
  await displayReceiptImage();
  const data = await getReceiptData();

  if (data) {
    document.querySelector("#receipt-id").value = data.data.transaction_pk;
    await displayReceiptData(data);
  }
}

async function handleReceiptSaving() {
  const data = {};

  // Get data
  data.transaction_pk = document.querySelector("#receipt-id").value;

  const receiptDataContainers = document.querySelectorAll(
    "#receipt-data-container .data-container.individual, #receipt-data-container .data-container.list"
  );

  receiptDataContainers.forEach((item) => {
    if (item.classList.contains("individual")) {
      if (item.querySelector("input").disabled) {
        return;
      }
      let variableName = item.getAttribute("data-variable-name");
      let value = item.querySelector("input").value;
      data[variableName] = value;
    } else {
      let variableName = item.getAttribute("data-variable-name");
      let itemLists = item.querySelector(".container");
      const inputs = itemLists.querySelectorAll("input");
      const values = Array.from(inputs).map((input) => input.value);
      data[variableName] = values;
    }
  });

  // Send data to server
  try {
    let response = await sendJSONgetJSON("/imports/update-receipt", data);
    appendAlert(response.message, "success");
  } catch (error) {
    appendAlert(error.message, "danger");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Add event listener to the Process Receipt button
  processButton.addEventListener("click", handleReceiptProcessing);

  // Add event listener to the camera button
  cameraButton.addEventListener("click", handleCameraUsage);

  // Add event listener to the file input for when a file is selected
  fileInput.addEventListener("change", handleFileSelection);

  // Add event listener to the Save Receipt button
  const saveButton = document.querySelector("#btn-save-receipt");
  saveButton.addEventListener("click", handleReceiptSaving);
});
