const rawBase = import.meta.env.VITE_API_BASE || (
  typeof window !== "undefined" && window.location.port === "5173"
    ? "http://localhost:8001/api"
    : "/api"
);

// Strip trailing slashes
const cleanBase = rawBase.replace(/\/+$/, "");

// Ensure API_BASE points to /api, while API_BASE_FALLBACK points to root
export const API_BASE = cleanBase.endsWith("/api") ? cleanBase : `${cleanBase}/api`;
export const API_BASE_FALLBACK = cleanBase.endsWith("/api") ? cleanBase.slice(0, -4) : cleanBase;

export async function fetchLunarDatasets() {
  let res = await fetch(`${API_BASE}/datasets`).catch(() => null);
  if (!res || !res.ok) {
    res = await fetch(`${API_BASE_FALLBACK}/datasets`).catch(() => null);
  }
  if (!res || !res.ok) throw new Error("Failed to fetch lunar datasets");
  return res.json();
}

export async function matchLunarImages(datasetId, method = "HYBRID_PHASE_CONGRUENCY", ransacThresh = 3.0, enableSubpixel = true) {
  const payload = JSON.stringify({
    dataset_id: datasetId,
    method: method,
    ransac_thresh: ransacThresh,
    enable_subpixel: enableSubpixel
  });

  let res = await fetch(`${API_BASE}/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: payload
  }).catch(() => null);

  if (!res || !res.ok) {
    res = await fetch(`${API_BASE_FALLBACK}/match`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload
    }).catch(() => null);
  }

  if (!res || !res.ok) throw new Error("Image correspondence matching failed");
  return res.json();
}

export async function fetchBenchmarkComparison(datasetId = "dataset_scale_ohrc_tmc2") {
  const res = await fetch(`${API_BASE}/benchmark?dataset_id=${datasetId}`);
  if (!res.ok) throw new Error("Failed to fetch benchmark comparison");
  return res.json();
}

export async function uploadAndMatchLunarImages(file1, file2, method = "HYBRID_PHASE_CONGRUENCY", ransacThresh = 3.0, enableSubpixel = true) {
  const formData = new FormData();
  formData.append("file1", file1);
  formData.append("file2", file2);
  formData.append("method", method);
  formData.append("ransac_thresh", ransacThresh);
  formData.append("enable_subpixel", enableSubpixel);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Custom image upload and matching failed" }));
    throw new Error(err.detail || "Upload matching failed");
  }
  return res.json();
}

export function getExportCsvUrl(datasetId) {
  return `${API_BASE}/export/csv?dataset_id=${datasetId}`;
}

export function getExportReportUrl(datasetId) {
  return `${API_BASE}/export/report?dataset_id=${datasetId}`;
}
