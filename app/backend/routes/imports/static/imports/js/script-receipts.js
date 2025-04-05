async function handleReceiptProcessing() {
  const fileInput = document.querySelector("#receipt-image");

  if (!fileInput.files || fileInput.files.length === 0) {
    alert("Please select a receipt image first");
    return;
  }

  const formData = new FormData();
  formData.append("receipt", fileInput.files[0]);

  try {
    const response = await fetch("/imports/from-receipts", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    // Handle the response data here
    console.log("Receipt processed successfully:", data);
  } catch (error) {
    console.error("Error processing receipt:", error);
    alert("Error processing receipt. Please try again.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const processButton = document.querySelector("#btn-process-receipt");
  processButton.addEventListener("click", handleReceiptProcessing);
});
