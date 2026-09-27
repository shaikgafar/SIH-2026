import React, { useState } from "react";
import { Sliders, Activity, Sparkles, Layers } from "lucide-react";

export default function RegistrationViewer({ img1Src, warpedImg2Src, diffSrc, overlaySrc, phase1Src, phase2Src }) {
  const [viewMode, setViewMode] = useState("SPLIT_SLIDER"); // SPLIT_SLIDER, DIFFERENCE, OVERLAY, PHASE
  const [sliderPos, setSliderPos] = useState(50); // percentage 0 to 100

  return (
    <div style={{
      background: "var(--bg-secondary)",
      borderRadius: "0.75rem",
      padding: "1.25rem",
      border: "1px solid var(--border-color)",
      display: "flex",
      flexDirection: "column",
      gap: "1rem"
    }}>
      {/* Header & View Switchers */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
        <div>
          <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff" }}>
            Sub-Pixel Registration & Alignment Verification
          </h3>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "2px" }}>
            Warped Image 2 is projected into Image 1 coordinates using the computed Homography matrix.
          </p>
        </div>

        <div style={{ display: "flex", gap: "0.35rem", background: "rgba(15, 23, 42, 0.8)", padding: "0.25rem", borderRadius: "0.45rem", border: "1px solid var(--border-color)" }}>
          {[
            { id: "SPLIT_SLIDER", label: "Split-Screen Curtain Wipe", icon: Sliders },
            { id: "OVERLAY", label: "Multi-Spectral Anaglyph", icon: Layers },
            { id: "DIFFERENCE", label: "Residual Difference Map", icon: Activity },
            { id: "PHASE", label: "Phase Congruency (Shadow Invariant)", icon: Sparkles },
          ].map((v) => {
            const Icon = v.icon;
            return (
              <button
                key={v.id}
                onClick={() => setViewMode(v.id)}
                style={{
                  fontSize: "0.72rem",
                  padding: "0.35rem 0.65rem",
                  borderRadius: "0.35rem",
                  border: "none",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.35rem",
                  background: viewMode === v.id ? "var(--accent-blue)" : "transparent",
                  color: viewMode === v.id ? "#ffffff" : "var(--text-muted)",
                  fontWeight: viewMode === v.id ? 600 : 400
                }}
              >
                <Icon size={12} /> {v.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Display Area */}
      <div style={{
        background: "#090d16",
        borderRadius: "0.55rem",
        border: "1px solid var(--border-color)",
        overflow: "hidden",
        position: "relative",
        minHeight: "460px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center"
      }}>
        {/* Mode 1: Split Slider */}
        {viewMode === "SPLIT_SLIDER" && (
          <div style={{ position: "relative", width: "100%", maxWidth: "512px", height: "512px", margin: "0 auto", overflow: "hidden", userSelect: "none" }}>
            {/* Background Image: Image 1 */}
            <img
              src={img1Src}
              alt="Image 1"
              style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", objectFit: "contain" }}
            />

            {/* Foreground Image: Warped Image 2 clipped by slider */}
            <div style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: `${sliderPos}%`,
              height: "100%",
              overflow: "hidden",
              borderRight: "3px solid #38bdf8",
              boxShadow: "2px 0 12px rgba(56, 189, 248, 0.6)"
            }}>
              <img
                src={warpedImg2Src}
                alt="Warped Image 2"
                style={{ width: "512px", height: "512px", maxWidth: "none", objectFit: "contain" }}
              />
            </div>

            {/* Slider Handle Badge */}
            <div style={{
              position: "absolute",
              top: "12px",
              left: `${sliderPos}%`,
              transform: "translateX(-50%)",
              background: "#0284c7",
              color: "#ffffff",
              padding: "0.2rem 0.5rem",
              borderRadius: "0.3rem",
              fontSize: "0.68rem",
              fontWeight: 700,
              pointerEvents: "none"
            }}>
              DRAG TO INSPECT ({sliderPos}%)
            </div>

            {/* Interactive Slider Input */}
            <input
              type="range"
              min="0"
              max="100"
              value={sliderPos}
              onChange={(e) => setSliderPos(e.target.value)}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                opacity: 0,
                cursor: "ew-resize",
                zIndex: 20
              }}
            />
          </div>
        )}

        {/* Mode 2: Multi-Spectral Overlay */}
        {viewMode === "OVERLAY" && (
          <div style={{ textAlign: "center", padding: "1rem" }}>
            <img
              src={overlaySrc}
              alt="Composite Overlay"
              style={{ maxHeight: "480px", maxWidth: "100%", borderRadius: "0.4rem", border: "1px solid rgba(255,255,255,0.1)" }}
            />
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.6rem" }}>
              <span style={{ color: "#4ade80", fontWeight: 600 }}>Green Channel = Image 1</span> |{" "}
              <span style={{ color: "#f472b6", fontWeight: 600 }}>Magenta Channel = Warped Image 2</span>. Coincident terrain features align as white/neutral.
            </div>
          </div>
        )}

        {/* Mode 3: Difference Map */}
        {viewMode === "DIFFERENCE" && (
          <div style={{ textAlign: "center", padding: "1rem" }}>
            <img
              src={diffSrc}
              alt="Difference Map"
              style={{ maxHeight: "480px", maxWidth: "100%", borderRadius: "0.4rem", border: "1px solid rgba(255,255,255,0.1)" }}
            />
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.6rem" }}>
              Jet Color Scale: Blue = Zero residual error (perfect alignment). Red = Significant residual variation or sun-shadow shift.
            </div>
          </div>
        )}

        {/* Mode 4: Phase Congruency Maps */}
        {viewMode === "PHASE" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", padding: "1rem", width: "100%", maxWidth: "900px" }}>
            <div style={{ textAlign: "center" }}>
              <img
                src={phase1Src || img1Src}
                alt="Phase 1"
                style={{ width: "100%", maxHeight: "380px", objectFit: "contain", borderRadius: "0.4rem", border: "1px solid var(--border-color)" }}
              />
              <div style={{ fontSize: "0.75rem", color: "var(--accent-cyan)", fontWeight: 600, marginTop: "0.4rem" }}>
                Image 1 Phase Congruency (Shadow-Free)
              </div>
            </div>
            <div style={{ textAlign: "center" }}>
              <img
                src={phase2Src || warpedImg2Src}
                alt="Phase 2"
                style={{ width: "100%", maxHeight: "380px", objectFit: "contain", borderRadius: "0.4rem", border: "1px solid var(--border-color)" }}
              />
              <div style={{ fontSize: "0.75rem", color: "var(--accent-amber)", fontWeight: 600, marginTop: "0.4rem" }}>
                Image 2 Phase Congruency (Shadow-Free)
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
