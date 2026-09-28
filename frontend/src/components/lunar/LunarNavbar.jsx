import React from "react";
import { Satellite, RotateCcw, Globe, ExternalLink, Sparkles } from "lucide-react";

const TABS = [
  { id: "overview",   label: "Overview" },
  { id: "datasets",   label: "Datasets" },
  { id: "results",    label: "Results" },
  { id: "benchmark",  label: "Benchmark" },
];

export default function LunarNavbar({ activeTab, setActiveTab, onResetDemo, method, setMethod }) {
  return (
    <header style={{
      background: "rgba(10,15,30,0.97)",
      borderBottom: "1px solid var(--border)",
      position: "sticky",
      top: 0,
      zIndex: 50,
      backdropFilter: "blur(12px)",
    }}>
      <div style={{
        maxWidth: "1440px",
        margin: "0 auto",
        padding: "0.75rem 1.5rem",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "0.75rem",
      }}>

        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.65rem" }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            filter: "drop-shadow(0 0 8px rgba(56, 189, 248, 0.45))",
          }}>
            <img src="/favicon.svg" alt="Moon Logo" style={{ width: "100%", height: "100%", objectFit: "contain" }} />
          </div>
          <div>
            <span style={{ fontWeight: 800, fontSize: "1rem", color: "var(--text)" }}>
              LunaAlign
            </span>
            <span className="badge badge-blue" style={{ marginLeft: "0.5rem", fontSize: "0.62rem" }}>
              SIH26166
            </span>
          </div>
        </div>

        {/* Tabs */}
        <nav style={{ display: "flex", gap: "0.25rem" }}>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: "0.4rem 0.85rem",
                borderRadius: "var(--radius-sm)",
                fontSize: "0.8rem",
                fontWeight: activeTab === tab.id ? 700 : 500,
                border: "none",
                cursor: "pointer",
                background: activeTab === tab.id ? "var(--bg-inner)" : "transparent",
                color: activeTab === tab.id ? "var(--accent)" : "var(--text-muted)",
                transition: "all 0.15s",
              }}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Controls */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
          {/* Method pills */}
          {method && setMethod && (
            <div style={{
              display: "flex",
              background: "var(--bg-inner)",
              padding: "0.18rem",
              borderRadius: "var(--radius-sm)",
              border: "1px solid var(--border)",
              gap: "0.18rem",
            }}>
              <button
                onClick={() => setMethod("HYBRID_PHASE_CONGRUENCY")}
                style={{
                  fontSize: "0.72rem",
                  padding: "0.22rem 0.6rem",
                  borderRadius: "var(--radius-sm)",
                  border: "none",
                  cursor: "pointer",
                  background: method === "HYBRID_PHASE_CONGRUENCY" ? "var(--accent)" : "transparent",
                  color: method === "HYBRID_PHASE_CONGRUENCY" ? "#fff" : "var(--text-muted)",
                  fontWeight: method === "HYBRID_PHASE_CONGRUENCY" ? 600 : 400,
                  display: "flex",
                  alignItems: "center",
                  gap: "0.25rem",
                }}
              >
                <Sparkles size={11} /> LunaAlign Hybrid
              </button>
              <button
                onClick={() => setMethod("CLASSICAL_SIFT")}
                style={{
                  fontSize: "0.72rem",
                  padding: "0.22rem 0.6rem",
                  borderRadius: "var(--radius-sm)",
                  border: "none",
                  cursor: "pointer",
                  background: method === "CLASSICAL_SIFT" ? "rgba(255,255,255,0.12)" : "transparent",
                  color: method === "CLASSICAL_SIFT" ? "#fff" : "var(--text-muted)",
                  fontWeight: method === "CLASSICAL_SIFT" ? 600 : 400,
                }}
              >
                SIFT Baseline
              </button>
            </div>
          )}

          <button
            onClick={onResetDemo}
            className="btn btn-outline btn-sm"
            style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}
          >
            <RotateCcw size={12} /> Reset
          </button>

          <a
            href="https://chmapbrowse.issdc.gov.in/"
            target="_blank"
            rel="noreferrer"
            className="btn btn-outline btn-sm"
            style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}
          >
            <Globe size={13} /> ISSDC <ExternalLink size={10} />
          </a>
        </div>
      </div>
    </header>
  );
}
