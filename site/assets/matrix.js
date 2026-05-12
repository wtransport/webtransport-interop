const MATRIX_CONFIG = {
  endpoints: {
    chrome: "Chrome",
    edge: "Edge",
    firefox: "Firefox",
    pywebtransport: "PyWebTransport",
    wtransport_interop_service: "WTransport Interoperability Service",
  },
  scenarios: {
    echo: "ECHO",
    devious_baton: "DEVIOUS BATON",
  },
  scenarioOrder: ["echo", "devious_baton"],
};

function groupResults(data, groupField, versionField) {
  const grouped = new Map();

  data.forEach((item) => {
    const key = item[groupField];
    if (!grouped.has(key)) {
      grouped.set(key, {
        name: MATRIX_CONFIG.endpoints[key] || key,
        version: "unknown",
        scenarios: {},
      });
    }

    const entry = grouped.get(key);
    if (entry.version === "unknown" && item[versionField] !== "unknown") {
      entry.version = item[versionField];
    }
    entry.scenarios[item.scenario_name] = item.verdict;
  });

  return Array.from(grouped.values());
}

function renderRow(impl) {
  const tagsHtml = MATRIX_CONFIG.scenarioOrder
    .filter((scenario) => impl.scenarios[scenario])
    .map(
      (scenario) =>
        `<span class="tag tag-${impl.scenarios[scenario]}">${MATRIX_CONFIG.scenarios[scenario]}</span>`,
    )
    .join("");

  const vText = impl.version === "unknown" ? "unknown" : `v${impl.version}`;

  return `
    <div class="endpoint-row">
      <div class="endpoint-name">
        ${impl.name} <span class="version-badge">${vText}</span>
      </div>
      <div class="scenario-tags">${tagsHtml}</div>
    </div>
  `;
}

async function loadMatrix() {
  try {
    const res = await fetch("matrix_result.json?t=" + Date.now());
    if (!res.ok) throw new Error("network response was not ok");
    const data = await res.json();

    const baselineRecord = data.results.find(
      (r) =>
        r.server_name === "wtransport_interop_service" &&
        r.server_version !== "unknown",
    );

    if (baselineRecord && baselineRecord.server_version) {
      const v = baselineRecord.server_version;
      document.getElementById("lib-version").textContent =
        v === "unknown" ? "unknown" : `v${v}`;
    } else {
      document.getElementById("lib-version").textContent = "unknown";
    }

    document.getElementById("harness-version").textContent =
      `v${data.meta.version}`;

    const d = new Date(data.meta.timestamp * 1000);
    const timeStr = `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}-${String(d.getUTCDate()).padStart(2, "0")} ${String(d.getUTCHours()).padStart(2, "0")}:${String(d.getUTCMinutes()).padStart(2, "0")} UTC`;

    document.getElementById("report-meta").innerHTML = `
      <div class="meta-pill">Protocol: <strong>${data.meta.protocol}</strong></div>
      <div class="meta-pill">Generated: <strong>${timeStr}</strong></div>
    `;

    const clientRowsData = data.results.filter(
      (r) => r.server_name === "wtransport_interop_service",
    );
    const clientRows = groupResults(
      clientRowsData,
      "client_name",
      "client_version",
    );

    const serverRowsData = data.results.filter(
      (r) =>
        r.client_name === "pywebtransport" &&
        r.server_name !== "wtransport_interop_service",
    );
    const serverRows = groupResults(
      serverRowsData,
      "server_name",
      "server_version",
    );

    document.getElementById("client-rows").innerHTML = clientRows
      .map(renderRow)
      .join("");
    document.getElementById("server-rows").innerHTML = serverRows
      .map(renderRow)
      .join("");
  } catch (err) {
    document.getElementById("report-meta").innerHTML = `
      <div class="meta-pill" style="color: var(--text-tertiary)">
        Status: <strong>unavailable</strong>
      </div>`;
  }
}

document.addEventListener("DOMContentLoaded", loadMatrix);
