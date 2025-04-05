import { appendAlert } from "../../../../../../static/js/alerts.js";
import { displayReceiptImage, getReceiptData } from "./script-receipts.js";

let stream = null;
const receiptDataContainer = document.querySelector("#receipt-data-container");

const fileInput = document.querySelector("#receipt-image");
const receiptCanvas = document.querySelector("#receipt-canvas");
const processButton = document.querySelector("#btn-process-receipt");
const cameraButton = document.querySelector("#btn-use-camera");

// More robust check for camera support
export function checkCameraSupport() {
  // Check for the standard MediaDevices API
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    return true;
  }

  // Check for older implementations
  if (navigator.getUserMedia) {
    return true;
  }

  // Check for webkit implementations
  if (navigator.webkitGetUserMedia) {
    return true;
  }

  // Check for moz implementations
  if (navigator.mozGetUserMedia) {
    return true;
  }

  return false;
}

const isMediaDevicesSupported = checkCameraSupport();

// If camera is not supported, hide the camera button
if (!isMediaDevicesSupported) {
  cameraButton.style.display = "none";
}

// Function to handle camera usage
export async function handleCameraUsage() {
  // Check if MediaDevices API is supported
  if (!isMediaDevicesSupported) {
    appendAlert(
      "Your browser or device doesn't support camera access. Please use the file upload option instead.",
      "warning"
    );
    return;
  }

  // Hide container to have more screen area
  receiptDataContainer.classList.add("d-none");

  try {
    // Try different methods to access the camera
    let mediaStream;

    try {
      // Modern browsers
      mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });
    } catch (e) {
      console.log("Standard getUserMedia failed, trying alternatives");

      // Try with older implementations
      if (navigator.getUserMedia) {
        mediaStream = await new Promise((resolve, reject) => {
          navigator.getUserMedia({ video: true }, resolve, reject);
        });
      } else if (navigator.webkitGetUserMedia) {
        mediaStream = await new Promise((resolve, reject) => {
          navigator.webkitGetUserMedia({ video: true }, resolve, reject);
        });
      } else if (navigator.mozGetUserMedia) {
        mediaStream = await new Promise((resolve, reject) => {
          navigator.mozGetUserMedia({ video: true }, resolve, reject);
        });
      } else {
        throw new Error("No camera API available");
      }
    }

    stream = mediaStream;

    // Create a video element to display the camera feed
    const video = document.createElement("video");
    video.setAttribute("autoplay", "");
    video.setAttribute("playsinline", "");
    video.srcObject = stream;

    // Replace the canvas with the video element
    const canvasContainer = receiptCanvas.parentElement;
    canvasContainer.innerHTML = "";
    canvasContainer.appendChild(video);

    // Add a capture button
    const captureButton = document.createElement("button");
    captureButton.className = "btn btn-primary mt-2";
    captureButton.innerHTML = '<i class="bi bi-camera"></i> Capture Receipt';
    captureButton.addEventListener("click", captureImage);
    canvasContainer.appendChild(captureButton);

    // Update the camera button text
    cameraButton.innerHTML = '<i class="bi bi-x-circle"></i> Cancel Camera';
    cameraButton.classList.remove("btn-primary");
    cameraButton.classList.add("btn-danger");
    cameraButton.removeEventListener("click", handleCameraUsage);
    cameraButton.addEventListener("click", stopCamera);
  } catch (error) {
    appendAlert("Error accessing camera: " + error.message, "danger");
    console.error("Camera error:", error);
  }
}

// Function to stop the camera
function stopCamera() {
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
    stream = null;

    // Restore the canvas
    const canvasContainer = document.querySelector(".text-center.mb-3");
    canvasContainer.innerHTML = "";
    canvasContainer.appendChild(receiptCanvas);

    // Reset the camera button
    cameraButton.innerHTML = '<i class="bi bi-camera"></i> Use my camera';
    cameraButton.classList.remove("btn-danger");
    cameraButton.classList.add("btn-primary");
    cameraButton.removeEventListener("click", stopCamera);
    cameraButton.addEventListener("click", handleCameraUsage);
  }
}

// Function to capture an image from the camera
async function captureImage() {
  if (!stream) return;

  // Create a temporary canvas to capture the image
  receiptDataContainer.classList.remove("d-none");

  const video = document.querySelector("video");
  const tempCanvas = document.createElement("canvas");
  tempCanvas.width = video.videoWidth;
  tempCanvas.height = video.videoHeight;
  const tempCtx = tempCanvas.getContext("2d");
  tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);

  // Convert the canvas to a blob
  const blob = await new Promise((resolve) =>
    tempCanvas.toBlob(resolve, "image/jpeg")
  );

  // Create a File object from the blob
  const file = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });

  // Create a FileList-like object
  const dataTransfer = new DataTransfer();
  dataTransfer.items.add(file);
  fileInput.files = dataTransfer.files;

  // Stop the camera
  stopCamera();

  // Process the captured image
  await displayReceiptImage();
  const data = await getReceiptData();

  if (data) {
    document.querySelector("#receipt-id").value = data.data.transaction_pk;
    await displayReceiptData(data);
  }
}
