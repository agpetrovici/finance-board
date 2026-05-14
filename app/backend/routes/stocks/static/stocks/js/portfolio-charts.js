const fmt = (v) => "$" + v.toFixed(2);
const fmtPct = (v) => v.toFixed(2) + "%";

function chartHeight(tall = 380, short = 260) {
  return window.innerWidth < 768 ? short : tall;
}

const LW = LightweightCharts;

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
// Helpers
// ---------------------------------------------------------------------------

/** Convert ApexCharts-style data points to {time, value} for Lightweight Charts. */
function toPoints(data) {
  return data.map((d) => {
    if (Array.isArray(d)) {
      const [t, v] = d;
      const time =
        typeof t === "number" ? new Date(t).toISOString().slice(0, 10) : t;
      return { time, value: v };
    }
    const t = d.x;
    const time =
      typeof t === "number" ? new Date(t).toISOString().slice(0, 10) : t;
    return { time, value: d.y };
  });
}

function lwChartBase(containerId, height = chartHeight()) {
  const container = document.getElementById(containerId);
  container.style.height = height + "px";

  const chart = LW.createChart(container, {
    layout: {
      background: { type: "solid", color: "transparent" },
      textColor:
        getComputedStyle(document.body)
          .getPropertyValue("--bs-body-color")
          .trim() || "#333",
    },
    grid: {
      vertLines: { color: "rgba(128,128,128,0.1)" },
      horzLines: { color: "rgba(128,128,128,0.1)" },
    },
    rightPriceScale: { borderVisible: false },
    timeScale: { borderVisible: false },
    crosshair: { mode: LW.CrosshairMode.Normal },
    localization: { priceFormatter: (p) => fmt(p) },
  });

  const resizeObserver = new ResizeObserver(() => {
    chart.applyOptions({ width: container.clientWidth });
  });
  resizeObserver.observe(container);

  return chart;
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
// Chart 1 – Portfolio Value vs Cost Basis (Lightweight Charts – Area)
// ---------------------------------------------------------------------------
function renderValueVsCostChart(data) {
  if (!data.series || data.series.length === 0) return;

  const chart = lwChartBase("chart-value-vs-cost");
  const colors = ["#008FFB", "#546E7A"];

  data.series.forEach((s, i) => {
    const color = colors[i % colors.length];
    const series = chart.addSeries(LW.AreaSeries, {
      title: s.name,
      lineColor: color,
      topColor: color + "55",
      bottomColor: "transparent",
      lineWidth: 2,
      priceLineVisible: false,
    });
    series.setData(toPoints(s.data));
  });

  chart.timeScale().fitContent();
}

// ---------------------------------------------------------------------------
// Chart 2 – Cumulative P&L (Lightweight Charts – Line + baseline)
// ---------------------------------------------------------------------------
function renderPnlChart(data) {
  if (!data.series || data.series.length === 0) return;

  const chart = lwChartBase("chart-pnl");
  const colors = ["#008FFB", "#00E396", "#263238"];

  data.series.forEach((s, i) => {
    const color = colors[i % colors.length];
    const isFirst = i === 0;

    const series = isFirst
      ? chart.addSeries(LW.BaselineSeries, {
          title: s.name,
          baseValue: { type: "price", price: 0 },
          topLineColor: "#00E396",
          topFillColor1: "rgba(0,227,150,0.28)",
          topFillColor2: "rgba(0,227,150,0.05)",
          bottomLineColor: "#FF4560",
          bottomFillColor1: "rgba(255,69,96,0.05)",
          bottomFillColor2: "rgba(255,69,96,0.28)",
          priceLineVisible: false,
        })
      : chart.addSeries(LW.LineSeries, {
          title: s.name,
          color: color,
          lineWidth: 2,
          priceLineVisible: false,
        });

    series.setData(toPoints(s.data));

    if (isFirst) {
      series.createPriceLine({
        price: 0,
        color: "#999",
        lineWidth: 1,
        lineStyle: LW.LineStyle.Dashed,
        axisLabelVisible: false,
        title: "Break-even",
      });
    }
  });

  chart.timeScale().fitContent();
}

// ---------------------------------------------------------------------------
// Chart 3 – Per-Stock Return % (ApexCharts – Horizontal Bar)
// ---------------------------------------------------------------------------
function renderStockPerformanceBars(data) {
  if (!data || data.length === 0) return;

  const sorted = [...data].sort((a, b) => a.return_pct - b.return_pct);
  const categories = sorted.map((d) => d.symbol);
  const values = sorted.map((d) => d.return_pct);
  const colors = values.map((v) => (v >= 0 ? "#00E396" : "#FF4560"));

  const options = {
    series: [{ name: "Return %", data: values }],
    chart: { type: "bar", height: chartHeight(30 * categories.length + 80, 20 * categories.length + 60) },
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
// Chart 4 – Portfolio Allocation (ApexCharts – Donut)
// ---------------------------------------------------------------------------
function renderAllocationDonut(data) {
  if (!data || data.length === 0) return;

  const labels = data.map((d) => d.symbol);
  const series = data.map((d) => d.value);

  const options = {
    series: series,
    chart: { type: "donut", height: chartHeight() },
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
// Chart 5 – Individual Stock Detail (Lightweight Charts – Area with selector)
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

  const chart = lwChartBase("chart-stock-detail");
  const colors = ["#008FFB", "#546E7A"];

  const seriesInstances = [
    chart.addSeries(LW.AreaSeries, {
      title: "Market Value",
      lineColor: colors[0],
      topColor: colors[0] + "55",
      bottomColor: "transparent",
      lineWidth: 2,
      priceLineVisible: false,
    }),
    chart.addSeries(LW.AreaSeries, {
      title: "Cost Basis",
      lineColor: colors[1],
      topColor: colors[1] + "55",
      bottomColor: "transparent",
      lineWidth: 2,
      priceLineVisible: false,
    }),
  ];

  function loadSymbol(sym) {
    const stockData = perStockSeries[sym];
    seriesInstances[0].setData(toPoints(stockData.market_value));
    seriesInstances[1].setData(toPoints(stockData.cost_basis));
    chart.timeScale().fitContent();
  }

  loadSymbol(symbols[0]);

  function onStockChange() {
    loadSymbol(select.value);
  }

  select.addEventListener("change", onStockChange);
}

// ---------------------------------------------------------------------------
// Chart 6 – Monthly Returns (ApexCharts – Column)
// ---------------------------------------------------------------------------
function renderMonthlyReturnsChart(data) {
  if (!data.categories || data.categories.length === 0) return;

  const colors = data.values.map((v) => (v >= 0 ? "#00E396" : "#FF4560"));

  const options = {
    series: [{ name: "Monthly Return", data: data.values }],
    chart: { type: "bar", height: chartHeight() },
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
