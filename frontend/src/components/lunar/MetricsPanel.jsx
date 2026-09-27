import React from "react";
import { Download, CheckCircle2, AlertTriangle, ShieldCheck, FileText } from "lucide-react";
import { getExportCsvUrl, getExportReportUrl } from "../../lunarApi";

function MetricCard({ label, value, sub, badgeClass, badgeText }) {
  return (
    <div className="card-inner" style={{ borderRadius: "var(--radius)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
        <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: 500 }}>{label}</span>
        {badgeClass && <span className={`badge ${badgeClass}`} style={{ fontSize: "0.62rem" }}>{badgeText}</span>}
      </div>
      <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--text)", lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>{sub}</div>}
    </div>
  );
}

export default function MetricsPanel({ metrics, datasetId }) {
  if (!metrics) return null;

  const level   = metrics.confidence_level || "MEDIUM";
  const isHigh  = level === "HIGH";
  const isMed   = level === "MEDIUM";
  const ConfIcon = isHigh ? CheckCircle2 : isMed ? ShieldCheck : AlertTriangle;
  const confColor = isHigh ? "var(--green)" : isMed ? "var(--amber)" : "var(--red)";
  const confBadge = isHigh ? "badge-green" : isMed ? "badge-amber" : "badge-red";

  const rmse         = metrics.rmse_pixels;
  const inlierPct    = Math.round((metrics.inlier_ratio || 0) * 100);
  const coverage     = metrics.spatial_coverage_pct ?? 0;
  const timeMs       = metrics.execution_time_ms;

  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.6rem" }}>
        <div>
          <h3 className="page-title">Results Summary</h3>
          <p className="page-sub">Key metrics from this alignment run.</p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <a href={getExportReportUrl(datasetId)} target="_blank" rel="noreferrer"
            className="btn btn-outline btn-sm" style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}>
            <FileText size={13} /> Export Report
          </a>
          <a href={getExportCsvUrl(datasetId)} target="_blank" rel="noreferrer"
            className="btn btn-outline btn-sm" style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}>
            <Download size={13} /> Export CSV
          </a>
        </div>
      </div>

      {/* Confidence verdict */}
      <div style={{
        background: isHigh ? "rgba(34,197,94,.08)" : isMed ? "rgba(245,158,11,.08)" : "rgba(239,68,68,.08)",
        border: `1px solid ${confColor}44`,
        borderRadius: "var(--radius-sm)",
        padding: "0.75rem 1rem",
        display: "flex",
        alignItems: "center",
        gap: "0.6rem",
      }}>
        <ConfIcon size={18} color={confColor} />
        <div>
          <div style={{ fontWeight: 700, fontSize: "0.9rem", color: "var(--text)" }}>
            {isHigh ? "High Confidence Alignment" : isMed ? "Medium Confidence Alignment" : level === "FAILED" ? "Alignment Failed" : "Low Confidence Alignment"}
            <span className={`badge ${confBadge}`} style={{ marginLeft: "0.5rem", fontSize: "0.62rem" }}>{level}</span>
          </div>
          <div style={{ fontSize: "0.76rem", color: "var(--text-muted)", marginTop: "2px" }}>
            {level === "FAILED"
              ? "Classical gradient SIFT breaks down under planetary shadow flips & scale shifts (<4 inliers). Switch to 'LunaAlign Hybrid' above for illumination-invariant phase matching."
              : (metrics.confidence_reason || "Evaluated against planetary registration tolerances.")}
          </div>
        </div>
      </div>

      {/* 2×2 Metric grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
        <MetricCard
          label="Alignment Accuracy"
          value={`${rmse} px`}
          sub={metrics.rmse_meters ? `≈ ${metrics.rmse_meters} m on ground` : "Lower is better"}
          badgeClass={rmse <= 2.0 ? "badge-green" : "badge-amber"}
          badgeText={rmse <= 2.0 ? "Excellent" : "Acceptable"}
        />
        <MetricCard
          label="Match Quality"
          value={`${inlierPct}%`}
          sub={`${metrics.inlier_count} of ${metrics.total_matches} matches kept`}
          badgeClass={inlierPct >= 30 ? "badge-green" : "badge-amber"}
          badgeText={inlierPct >= 30 ? "Good" : "Low"}
        />
        <MetricCard
          label="Image Coverage"
          value={`${coverage}%`}
          sub={metrics.clustering_detected ? "Matches clustered — may be less reliable" : "Well spread across image"}
          badgeClass={metrics.clustering_detected ? "badge-red" : "badge-green"}
          badgeText={metrics.clustering_detected ? "Clustered" : "Uniform"}
        />
        <MetricCard
          label="Processing Speed"
          value={timeMs ? `${timeMs} ms` : "—"}
          sub={metrics.hardware_processor || "CPU"}
          badgeClass="badge-blue"
          badgeText="Speed"
        />
      </div>
    </div>
  );
}
