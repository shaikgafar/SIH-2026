import React, { useState, useEffect } from "react";
import { BarChart3, RefreshCw, Sparkles } from "lucide-react";
import { fetchBenchmarkComparison } from "../../lunarApi";

export default function AlgorithmBenchmark({ datasetId }) {
  const [data, setData]       = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const load = async (id) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetchBenchmarkComparison(id);
      setData(Array.isArray(res) ? res : res?.results || []);
    } catch (err) {
      setError("Could not load benchmark: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(datasetId); }, [datasetId]);

  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.6rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <BarChart3 size={18} color="var(--accent)" />
          <div>
            <h3 className="page-title">Algorithm Comparison</h3>
            <p className="page-sub">LunaAlign Hybrid vs standard methods — live results on the same dataset.</p>
          </div>
        </div>
        <button onClick={() => load(datasetId)} disabled={loading} className="btn btn-outline btn-sm"
          style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}>
          <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
          {loading ? "Running…" : "Re-run"}
        </button>
      </div>

      {/* Disclaimer */}
      <div className="toast">
        <strong>Note:</strong> Only algorithms marked "Live" ran on your selected image pair.
        Planned entries are listed for reference only — no fabricated scores.
      </div>

      {error && <div className="toast toast-error">{error}</div>}

      {/* Table */}
      <div style={{ overflowX: "auto" }}>
        <table className="simple-table">
          <thead>
            <tr>
              <th>Algorithm</th>
              <th>Status</th>
              <th>Match Quality</th>
              <th>Alignment Accuracy</th>
              <th>Image Coverage</th>
              <th>Speed (ms)</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {loading && data.length === 0 && (
              <tr>
                <td colSpan={7} style={{ textAlign: "center", color: "var(--text-muted)", padding: "2rem" }}>
                  Running benchmark…
                </td>
              </tr>
            )}
            {data.map((row, i) => {
              const isLuna = row.algorithm?.includes("LunaAlign");
              const isLive = row.status === "IMPLEMENTED";
              return (
                <tr key={i} style={{ background: isLuna ? "rgba(56,189,248,.05)" : "transparent" }}>
                  <td style={{ fontWeight: isLuna ? 700 : 500, color: isLuna ? "var(--accent)" : "var(--text)" }}>
                    {isLuna && <Sparkles size={12} style={{ marginRight: "0.3rem", verticalAlign: "middle" }} />}
                    {row.algorithm}
                  </td>
                  <td>
                    <span className={`badge ${isLive ? "badge-green" : "badge-amber"}`}>
                      {isLive ? "Live" : "Planned"}
                    </span>
                  </td>
                  <td>{isLive && row.inlier_ratio != null ? `${(row.inlier_ratio * 100).toFixed(1)}%` : "—"}</td>
                  <td>{isLive && row.rmse_pixels  != null ? `${row.rmse_pixels.toFixed(2)} px` : "—"}</td>
                  <td>{isLive && row.spatial_coverage_pct != null ? `${row.spatial_coverage_pct}%` : "—"}</td>
                  <td>{isLive && row.runtime_ms   != null ? `${Math.round(row.runtime_ms)}` : "—"}</td>
                  <td style={{ color: "var(--text-muted)", fontSize: "0.78rem" }}>
                    {row.notes ? row.notes.split(".")[0] : "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Plain-language insight */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.85rem" }}>
        <div className="card-inner" style={{ borderRadius: "var(--radius-sm)" }}>
          <strong style={{ fontSize: "0.8rem", color: "var(--text)", display: "block", marginBottom: "0.3rem" }}>
            Why standard SIFT struggles on the Moon
          </strong>
          <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", margin: 0, lineHeight: 1.55 }}>
            When sun angle changes, crater shadows flip direction. Standard feature detectors rely on brightness gradients, which flip too — causing false matches.
          </p>
        </div>
        <div className="card-inner" style={{ borderRadius: "var(--radius-sm)" }}>
          <strong style={{ fontSize: "0.8rem", color: "var(--accent)", display: "block", marginBottom: "0.3rem" }}>
            How LunaAlign Hybrid fixes this
          </strong>
          <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", margin: 0, lineHeight: 1.55 }}>
            Smart Feature Detection looks at where image frequencies agree — not just brightness — so landmarks stay detectable even when lighting changes completely.
          </p>
        </div>
      </div>
    </div>
  );
}
