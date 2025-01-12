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
    throw new Error(data.body || "Network response was not ok.");
  }

  return data;
}
