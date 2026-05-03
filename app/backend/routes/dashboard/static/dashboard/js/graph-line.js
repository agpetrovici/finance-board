const SERIES_COLORS = [
  "#2962FF",
  "#e15759",
  "#f28e2c",
  "#76b7b2",
  "#59a14f",
  "#edc948",
  "#b07aa1",
  "#ff9da7",
  "#9c755f",
  "#bab0ac",
];

export function graphLine(seriesData, selector = "#finance-chart") {
  const container = document.querySelector(selector);

  const chart = LightweightCharts.createChart(container, {
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
    rightPriceScale: {
      borderVisible: false,
    },
    timeScale: {
      borderVisible: false,
      timeVisible: false,
    },
    crosshair: {
      mode: LightweightCharts.CrosshairMode.Normal,
    },
    localization: {
      priceFormatter: (price) => price.toFixed(2),
    },
  });

  seriesData.forEach((s, index) => {
    const color = SERIES_COLORS[index % SERIES_COLORS.length];
    const isTotal = index === 0;

    const series = chart.addSeries(LightweightCharts.AreaSeries, {
      title: s.name,
      lineColor: color,
      topColor: isTotal ? `${color}44` : "transparent",
      bottomColor: "transparent",
      lineWidth: isTotal ? 2 : 1,
      priceLineVisible: false,
      lastValueVisible: true,
      crosshairMarkerVisible: true,
    });

    const points = s.data.map(([time, value]) => ({ time, value }));
    series.setData(points);
  });

  chart.timeScale().fitContent();

  const resizeObserver = new ResizeObserver(() => {
    chart.applyOptions({ width: container.clientWidth });
  });
  resizeObserver.observe(container);
}
