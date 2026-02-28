import { getJSON } from "../../../../../static/js/fetch.js";

document.addEventListener("DOMContentLoaded", initIncomeExpensesChart);

let chart = null;

async function initIncomeExpensesChart() {
  const data = await getJSON("/api/get-income-expenses");
  if (!data.length) return;

  const monthSelect = document.getElementById("month-select");
  data.forEach(function populateOption(statement, index) {
    const option = document.createElement("option");
    option.value = index;
    const date = new Date(statement.month + "T00:00:00");
    option.textContent = date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
    });
    monthSelect.appendChild(option);
  });

  monthSelect.value = data.length - 1;
  renderChart(data[data.length - 1]);

  monthSelect.addEventListener("change", handleMonthChange);

  function handleMonthChange() {
    renderChart(data[this.value]);
  }
}

const INCOME_COLORS = [
  "#00E396",
  "#00B87A",
  "#2E93fA",
  "#66DA26",
  "#26a69a",
  "#00D68F",
  "#3BCEAC",
  "#0EAD69",
];
const EXPENSE_COLORS = [
  "#FF4560",
  "#FF6178",
  "#FEB019",
  "#FF6C37",
  "#D10CE8",
  "#775DD0",
  "#E84855",
  "#F77F00",
];

function buildSeries(statement) {
  const series = [];
  const colors = [];
  let incomeColorIdx = 0;
  let expenseColorIdx = 0;

  statement.incomes.forEach(function (cat) {
    cat.subcategories.forEach(function (sub) {
      series.push({
        name: cat.name + " \u203a " + sub.name,
        data: [sub.amount, 0, 0, 0],
      });
      colors.push(INCOME_COLORS[incomeColorIdx % INCOME_COLORS.length]);
      incomeColorIdx++;
    });
  });

  statement.incomes.forEach(function (cat) {
    const total = cat.subcategories.reduce(function (sum, sub) {
      return sum + sub.amount;
    }, 0);
    series.push({
      name: cat.name,
      data: [0, Math.round(total * 100) / 100, 0, 0],
    });
    colors.push(INCOME_COLORS[incomeColorIdx % INCOME_COLORS.length]);
    incomeColorIdx++;
  });

  statement.expenses.forEach(function (cat) {
    const total = cat.subcategories.reduce(function (sum, sub) {
      return sum + Math.abs(sub.amount);
    }, 0);
    series.push({
      name: cat.name,
      data: [0, 0, Math.round(total * 100) / 100, 0],
    });
    colors.push(EXPENSE_COLORS[expenseColorIdx % EXPENSE_COLORS.length]);
    expenseColorIdx++;
  });

  statement.expenses.forEach(function (cat) {
    cat.subcategories.forEach(function (sub) {
      series.push({
        name: cat.name + " \u203a " + sub.name,
        data: [0, 0, 0, Math.abs(sub.amount)],
      });
      colors.push(EXPENSE_COLORS[expenseColorIdx % EXPENSE_COLORS.length]);
      expenseColorIdx++;
    });
  });

  return { series, colors };
}

function renderChart(statement) {
  const { series, colors } = buildSeries(statement);

  if (chart) {
    chart.destroy();
  }

  const options = {
    chart: {
      type: "bar",
      height: 550,
      stacked: true,
      toolbar: { show: true },
    },
    plotOptions: {
      bar: { horizontal: false, columnWidth: "70%" },
    },
    colors: colors,
    series: series,
    xaxis: {
      categories: [
        ["Income", "(Subcategories)"],
        ["Income", "(Categories)"],
        ["Expenses", "(Categories)"],
        ["Expenses", "(Subcategories)"],
      ],
    },
    yaxis: {
      title: { text: "Amount (€)" },
      labels: {
        formatter: function (val) {
          return val.toFixed(2);
        },
      },
    },
    title: {
      text: "Income vs Expenses",
      align: "left",
    },
    legend: { position: "bottom" },
    dataLabels: { enabled: false },
    tooltip: {
      y: {
        formatter: function (val) {
          return val.toFixed(2) + " €";
        },
      },
    },
  };

  chart = new ApexCharts(
    document.querySelector("#chart-income-expenses"),
    options
  );
  chart.render();
}
