import { graph_line } from "./graph_line.js";

document.addEventListener("DOMContentLoaded", function () {
  // Sample data
  const data = {
    datasets: [
      {
        borderColor: "rgb(75, 192, 192)",
        data: [1500, 2000, 1800, 2200, 2600, 2400],
        label: "Income",
        tension: 0.1,
      },
      {
        borderColor: "rgb(255, 99, 132)",
        data: [1200, 1800, 1600, 2000, 2200, 2100],
        label: "Expenses",
        tension: 0.1,
      },
    ],
    labels: ["January", "February", "March", "April", "May", "June"],
  };

  graph_line(data);
});
