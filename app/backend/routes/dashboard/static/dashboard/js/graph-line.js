export async function graphLine(data) {
  // Get the canvas element
  const ctx = document.getElementById("financeChart").getContext("2d");

  // Chart configuration
  const config = {
    type: "line",
    data: data,
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "Monthly Financial Overview",
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Amount ($)",
          },
        },
      },
    },
  };

  // Create the chart
  new Chart(ctx, config);
}
