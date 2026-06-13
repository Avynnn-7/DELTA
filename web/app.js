const ARTIFACT_URL = "data/artifacts.json";
const SVG_NS = "http://www.w3.org/2000/svg";

function formatNumber(value) {
  if (typeof value !== "number" || !isFinite(value)) {
    return String(value);
  }
  return value.toLocaleString(undefined, {
    minimumFractionDigits: 4,
    maximumFractionDigits: 4
  });
}

function formatVector(values) {
  return values.map(formatNumber).join(", ");
}

function axisRange(values) {
  let low = values[0];
  let high = values[0];
  for (const value of values) {
    if (value < low) {
      low = value;
    }
    if (value > high) {
      high = value;
    }
  }
  return { low, high };
}

function svgElement(name, attributes) {
  const node = document.createElementNS(SVG_NS, name);
  for (const key in attributes) {
    node.setAttribute(key, attributes[key]);
  }
  return node;
}

function renderPositionInspector(positionMetrics) {
  const body = document.querySelector("#position-table tbody");
  body.replaceChildren();
  Object.keys(positionMetrics).forEach((metric) => {
    const row = document.createElement("tr");
    const label = document.createElement("td");
    label.textContent = metric;
    const value = document.createElement("td");
    value.textContent = formatVector(positionMetrics[metric]);
    row.append(label, value);
    body.append(row);
  });
}

function renderCurve(container, title, curve) {
  const heading = document.createElement("p");
  heading.className = "chart-title";
  heading.textContent = title;
  container.append(heading);

  const width = 320;
  const height = 120;
  const svg = svgElement("svg", { viewBox: `0 0 ${width} ${height}` });
  const { low, high } = axisRange(curve);
  const span = high - low || 1;
  const step = curve.length > 1 ? width / (curve.length - 1) : width;
  const points = curve
    .map((value, index) => {
      const x = index * step;
      const y = height - ((value - low) / span) * height;
      return `${x},${y}`;
    })
    .join(" ");
  svg.append(svgElement("polyline", { points, fill: "none", stroke: "#4493f8", "stroke-width": "1.5" }));
  container.append(svg);
}

function renderSurvival(survivalCurves) {
  const container = document.querySelector("#survival-charts");
  container.replaceChildren();
  Object.keys(survivalCurves).forEach((name) => {
    renderCurve(container, name, survivalCurves[name]);
  });
}

function renderRiskSummary(artifacts) {
  const summary = document.querySelector("#risk-summary");
  summary.replaceChildren();
  const rows = [
    ["Confidence level", artifacts.alpha],
    ["Value at Risk", artifacts.value_at_risk],
    ["Expected Shortfall", artifacts.expected_shortfall]
  ];
  rows.forEach(([label, value]) => {
    const term = document.createElement("dt");
    term.textContent = label;
    const detail = document.createElement("dd");
    detail.textContent = formatNumber(value);
    summary.append(term, detail);
  });
}

function renderLossDensity(artifacts) {
  const container = document.querySelector("#loss-histogram");
  container.replaceChildren();

  const edges = artifacts.loss_histogram.edges;
  const density = artifacts.loss_histogram.density;
  const width = 360;
  const height = 160;
  const svg = svgElement("svg", { viewBox: `0 0 ${width} ${height}` });

  const minEdge = edges[0];
  const maxEdge = edges[edges.length - 1];
  const edgeSpan = maxEdge - minEdge || 1;
  const maxDensity = axisRange(density).high || 1;

  density.forEach((value, index) => {
    const left = ((edges[index] - minEdge) / edgeSpan) * width;
    const right = ((edges[index + 1] - minEdge) / edgeSpan) * width;
    const barHeight = (value / maxDensity) * height;
    svg.append(
      svgElement("rect", {
        class: "histogram-bar",
        x: left,
        y: height - barHeight,
        width: Math.max(right - left - 1, 0),
        height: barHeight
      })
    );
  });

  const marker = (position, className) => {
    const x = ((position - minEdge) / edgeSpan) * width;
    svg.append(svgElement("line", { class: className, x1: x, y1: 0, x2: x, y2: height }));
  };
  marker(artifacts.value_at_risk, "marker-var");
  marker(artifacts.expected_shortfall, "marker-es");

  container.append(svg);
}

function renderContagion(contributions) {
  const container = document.querySelector("#contribution-bars");
  container.replaceChildren();
  const { high } = axisRange(contributions);
  const scale = high || 1;
  contributions.forEach((value, index) => {
    const row = document.createElement("div");
    row.className = "bar-row";

    const label = document.createElement("span");
    label.textContent = `Position ${index}`;

    const track = document.createElement("div");
    track.className = "bar-track";
    const fill = document.createElement("div");
    fill.className = "bar-fill";
    fill.style.width = `${(value / scale) * 100}%`;
    track.append(fill);

    const amount = document.createElement("span");
    amount.textContent = formatNumber(value);

    row.append(label, track, amount);
    container.append(row);
  });
}

function render(artifacts) {
  renderPositionInspector(artifacts.position_metrics);
  renderSurvival(artifacts.survival_curves);
  renderRiskSummary(artifacts);
  renderLossDensity(artifacts);
  renderContagion(artifacts.es_contributions);
  document.querySelector("#schema-version").textContent = `Artifact schema version ${artifacts.schema_version}`;
}

async function main() {
  const response = await fetch(ARTIFACT_URL);
  const artifacts = await response.json();
  render(artifacts);
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", main);
}
