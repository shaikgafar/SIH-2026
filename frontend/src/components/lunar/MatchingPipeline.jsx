import React from "react";
import { CheckCircle2, Clock, AlertTriangle } from "lucide-react";

const STEPS = [
  { key: "load",     label: "Load Images" },
  { key: "detect",   label: "Smart Feature Detection" },
  { key: "match",    label: "Find Matches" },
  { key: "filter",   label: "Quality Filter" },
  { key: "align",    label: "Align & Fine-tune" },
];

function statusOf(key, metrics, loading) {
  if (loading) return "running";
  if (!metrics) return "pending";
  switch (key) {
    case "load":
    case "detect":
      return "done";
    case "match":
      return (metrics.total_matches || 0) > 0 ? "done" : "warn";
    case "filter":
      return (metrics.inlier_count || 0) >= 4 ? "done" : "warn";
    case "align":
      return metrics.confidence_level === "LOW" ? "warn" : "done";
    default:
      return "done";
  }
}

function StepIcon({ status }) {
  if (status === "running") return <Clock size={15} color="var(--accent)" className="animate-spin" />;
  if (status === "warn")    return <AlertTriangle size={15} color="var(--amber)" />;
  if (status === "done")    return <CheckCircle2 size={15} color="var(--green)" />;
  return <div style={{ width: 15, height: 15, borderRadius: "50%", background: "var(--border)" }} />;
}

export default function MatchingPipeline({ metrics, loading }) {
  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.85rem" }}>
        <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--text)" }}>
          Processing Pipeline
        </span>
        {metrics?.execution_time_ms && (
          <span className="chip chip-blue">{metrics.execution_time_ms} ms</span>
        )}
      </div>

      {/* Horizontal step row */}
      <div style={{ display: "flex", alignItems: "center", gap: 0, overflowX: "auto" }}>
        {STEPS.map((step, i) => {
          const status = statusOf(step.key, metrics, loading);
          const isLast = i === STEPS.length - 1;
          return (
            <React.Fragment key={step.key}>
              {/* Step bubble */}
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.35rem", minWidth: "5.5rem" }}>
                <div style={{
                  width: 34,
                  height: 34,
                  borderRadius: "50%",
                  background: "var(--bg-inner)",
                  border: `2px solid ${status === "done" ? "var(--green)" : status === "warn" ? "var(--amber)" : status === "running" ? "var(--accent)" : "var(--border)"}`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}>
                  <StepIcon status={status} />
                </div>
                <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textAlign: "center", lineHeight: 1.3 }}>
                  {step.label}
                </span>
              </div>
              {/* Connector line */}
              {!isLast && (
                <div style={{ flex: 1, height: 2, background: "var(--border)", minWidth: "1rem", marginBottom: "1.1rem" }} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
