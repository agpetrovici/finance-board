export async function getJSON(endpoint) {
  // Send a POST request to the endpoint with the object as JSON
  let response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
  // Read the response as json
  let data = await response.json();

  // Check if the response is OK (status 200-299)
  if (!response.ok) {
    throw new Error(data.message || "Network response was not ok.");
  }

  return data;
}

export async function sendJSONgetJSON(endpoint, object) {
  // Send a POST request to the endpoint with the object as JSON
  let response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(object),
  });
  // Read the response as json
  let data = await response.json();

  // Check if the response is OK (status 200-299)
  if (!response.ok) {
    throw new Error(data.message || "Network response was not ok.");
  }

  return data;
}

export async function sendFilegetJSON(endpoint, inputFileId) {
  // Get the file from the input element
  const fileInput = document.querySelector(inputFileId);
  const file = fileInput.files[0];

  if (!file) {
    throw new Error("No file selected");
  }

  // Create FormData and append file
  const formData = new FormData();
  formData.append("file", file);

  // Send POST request with FormData
  const response = await fetch(endpoint, {
    method: "POST",
    body: formData,
  });

  // Read the response as json
  const data = await response.json();

  // Check if response is OK (status 200-299)
  if (!response.ok) {
    throw new Error(
      data.messages || data.message || "Network response was not ok."
    );
  }

  return data;
}
