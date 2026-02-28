const fmt = (v) => "$" + v.toFixed(2);
const fmtPct = (v) => v.toFixed(2) + "%";

document.addEventListener("DOMContentLoaded", initPortfolioCharts);

async function initPortfolioCharts() {
  const response = await fetch("/api/get-portfolio-performance", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  const data = await response.json();

  renderSummaryCards(data.summary);
  renderValueVsCostChart(data.value_vs_cost);
  renderAllocationDonut(data.allocation);
  renderPnlChart(data.pnl_series);
  renderStockPerformanceBars(data.stock_performance);
  renderStockDetailChart(data.per_stock_series);
  renderMonthlyReturnsChart(data.monthly_returns);
}

// ---------------------------------------------------------------------------
// KPI Summary Cards
// ---------------------------------------------------------------------------
function renderSummaryCards(summary) {
  document.getElementById("kpi-invested").textContent = fmt(
    summary.total_invested,
  );
  document.getElementById("kpi-market-value").textContent = fmt(
    summary.total_market_value,
  );

  const returnEl = document.getElementById("kpi-total-return");
  returnEl.textContent = fmt(summary.total_return);
  returnEl.classList.add(
    summary.total_return >= 0 ? "text-success" : "text-danger",
  );

  const pctEl = document.getElementById("kpi-return-pct");
  pctEl.textContent = fmtPct(summary.total_return_pct);
  pctEl.classList.add(
    summary.total_return_pct >= 0 ? "text-success" : "text-danger",
  );
}

// ---------------------------------------------------------------------------
// Chart 1 – Portfolio Value vs Cost Basis (Area)
// ---------------------------------------------------------------------------
function renderValueVsCostChart(data) {
  if (!data.series || data.series.length === 0) return;

  const options = {
    series: data.series,
    chart: {
      type: "area",
      height: 380,
      zoom: { type: "x", enabled: true, autoScaleYaxis: true },
      toolbar: { autoSelected: "zoom" },
    },
    colors: ["#008FFB", "#546E7A"],
    dataLabels: { enabled: false },
    markers: { size: 0 },
    stroke: { curve: "straight", width: 2 },
    fill: {
      type: "gradient",
      gradient: {
        shadeIntensity: 1,
        inverseColors: false,
        opacityFrom: 0.45,
        opacityTo: 0.05,
        stops: [0, 90, 100],
      },
    },
    xaxis: { type: "datetime" },
    yaxis: {
      labels: { formatter: (v) => fmt(v) },
      title: { text: "Value (USD)" },
    },
    tooltip: { shared: true, y: { formatter: (v) => fmt(v) } },
    legend: { position: "top" },
  };

  const chart = new ApexCharts(
    document.querySelector("#chart-value-vs-cost"),
    options,
  );
  chart.render();
}

// ---------------------------------------------------------------------------
// Chart 2 – Cumulative P&L (Line)
// ---------------------------------------------------------------------------
function renderPnlChart(data) {
  if (!data.series || data.series.length === 0) return;

  const options = {
    series: data.series,
    chart: {
      type: "line",
      height: 380,
      zoom: { type: "x", enabled: true, autoScaleYaxis: true },
      toolbar: { autoSelected: "zoom" },
    },
    colors: ["#008FFB", "#00E396", "#263238"],
    dataLabels: { enabled: false },
    stroke: { curve: "straight", width: [2, 2, 3] },
    markers: { size: 0 },
    xaxis: { type: "datetime" },
    yaxis: {
      labels: { formatter: (v) => fmt(v) },
      title: { text: "P&L (USD)" },
    },
    annotations: {
      yaxis: [
        {
          y: 0,
          borderColor: "#999",
          strokeDashArray: 4,
          label: {
            text: "Break-even",
            position: "front",
            style: { background: "#fff", fontSize: "11px" },
          },
        },
      ],
    },
    tooltip: { shared: true, y: { formatter: (v) => fmt(v) } },
    legend: { position: "top" },
  };

  const chart = new ApexCharts(document.querySelector("#chart-pnl"), options);
  chart.render();
}

// ---------------------------------------------------------------------------
// Chart 3 – Per-Stock Return % (Horizontal Bar)
// ---------------------------------------------------------------------------
function renderStockPerformanceBars(data) {
  if (!data || data.length === 0) return;

  const sorted = [...data].sort((a, b) => a.return_pct - b.return_pct);
  const categories = sorted.map((d) => d.symbol);
  const values = sorted.map((d) => d.return_pct);
  const colors = values.map((v) => (v >= 0 ? "#00E396" : "#FF4560"));

  const options = {
    series: [{ name: "Return %", data: values }],
    chart: { type: "bar", height: 30 * categories.length + 80 },
    plotOptions: {
      bar: { horizontal: true, barHeight: "60%", distributed: true },
    },
    colors: colors,
    dataLabels: {
      enabled: true,
      formatter: (v) => fmtPct(v),
      style: { fontSize: "11px" },
    },
    xaxis: {
      categories: categories,
      labels: { formatter: (v) => fmtPct(v) },
    },
    yaxis: { labels: { style: { fontSize: "12px" } } },
    tooltip: {
      y: {
        formatter: (_v, { dataPointIndex }) => {
          const d = sorted[dataPointIndex];
          return `P&L: ${fmt(d.total_pnl)} | Value: ${fmt(d.market_value)} | Cost: ${fmt(d.cost_basis)}`;
        },
      },
    },
    legend: { show: false },
  };

  const chart = new ApexCharts(
    document.querySelector("#chart-stock-performance"),
    options,
  );
  chart.render();
}

// ---------------------------------------------------------------------------
// Chart 4 – Portfolio Allocation (Donut)
// ---------------------------------------------------------------------------
function renderAllocationDonut(data) {
  if (!data || data.length === 0) return;

  const labels = data.map((d) => d.symbol);
  const series = data.map((d) => d.value);

  const options = {
    series: series,
    chart: { type: "donut", height: 380 },
    labels: labels,
    dataLabels: {
      enabled: true,
      formatter: (val) => fmtPct(val),
    },
    tooltip: {
      y: { formatter: (v) => fmt(v) },
    },
    legend: { position: "bottom", fontSize: "12px" },
    plotOptions: {
      pie: {
        donut: {
          labels: {
            show: true,
            total: {
              show: true,
              label: "Total",
              formatter: (w) =>
                fmt(w.globals.seriesTotals.reduce((a, b) => a + b, 0)),
            },
          },
        },
      },
    },
  };

  const chart = new ApexCharts(
    document.querySelector("#chart-allocation"),
    options,
  );
  chart.render();
}

// ---------------------------------------------------------------------------
// Chart 5 – Individual Stock Detail (Area with selector)
// ---------------------------------------------------------------------------
function renderStockDetailChart(perStockSeries) {
  const symbols = Object.keys(perStockSeries);
  if (symbols.length === 0) return;

  const select = document.getElementById("stock-select");
  symbols.forEach((sym) => {
    const opt = document.createElement("option");
    opt.value = sym;
    opt.textContent = sym;
    select.appendChild(opt);
  });

  let chartInstance = null;

  function buildOptions(symbol) {
    const stockData = perStockSeries[symbol];
    return {
      series: [
        { name: "Market Value", data: stockData.market_value },
        { name: "Cost Basis", data: stockData.cost_basis },
      ],
      chart: {
        type: "area",
        height: 380,
        zoom: { type: "x", enabled: true, autoScaleYaxis: true },
        toolbar: { autoSelected: "zoom" },
      },
      colors: ["#008FFB", "#546E7A"],
      dataLabels: { enabled: false },
      markers: { size: 0 },
      stroke: { curve: "straight", width: 2 },
      fill: {
        type: "gradient",
        gradient: {
          shadeIntensity: 1,
          inverseColors: false,
          opacityFrom: 0.45,
          opacityTo: 0.05,
          stops: [0, 90, 100],
        },
      },
      xaxis: { type: "datetime" },
      yaxis: {
        labels: { formatter: (v) => fmt(v) },
        title: { text: "Value (USD)" },
      },
      tooltip: { shared: true, y: { formatter: (v) => fmt(v) } },
      legend: { position: "top" },
    };
  }

  chartInstance = new ApexCharts(
    document.querySelector("#chart-stock-detail"),
    buildOptions(symbols[0]),
  );
  chartInstance.render();

  function onStockChange() {
    const sym = select.value;
    const stockData = perStockSeries[sym];
    chartInstance.updateSeries([
      { name: "Market Value", data: stockData.market_value },
      { name: "Cost Basis", data: stockData.cost_basis },
    ]);
  }

  select.addEventListener("change", onStockChange);
}

// ---------------------------------------------------------------------------
// Chart 6 – Monthly Returns (Column)
// ---------------------------------------------------------------------------
function renderMonthlyReturnsChart(data) {
  if (!data.categories || data.categories.length === 0) return;

  const colors = data.values.map((v) => (v >= 0 ? "#00E396" : "#FF4560"));

  const options = {
    series: [{ name: "Monthly Return", data: data.values }],
    chart: { type: "bar", height: 380 },
    plotOptions: { bar: { distributed: true, columnWidth: "70%" } },
    colors: colors,
    dataLabels: { enabled: false },
    xaxis: {
      categories: data.categories,
      labels: { rotate: -45, style: { fontSize: "11px" } },
    },
    yaxis: {
      labels: { formatter: (v) => fmt(v) },
      title: { text: "Return (USD)" },
    },
    annotations: {
      yaxis: [{ y: 0, borderColor: "#999", strokeDashArray: 4 }],
    },
    tooltip: { y: { formatter: (v) => fmt(v) } },
    legend: { show: false },
  };

  const chart = new ApexCharts(
    document.querySelector("#chart-monthly-returns"),
    options,
  );
  chart.render();
}
