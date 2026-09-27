import React, { useRef, useEffect, useState } from "react";
import { Eye, Filter, CheckCircle2, XCircle, Grid, Info, MousePointerClick, X } from "lucide-react";

export default function TiePointCanvas({ img1Src, img2Src, tiePoints = [], datasetInfo, spatialCoveragePct }) {
  const canvasRef = useRef(null);
  const [filterMode, setFilterMode] = useState("ALL"); // ALL, INLIERS, OUTLIERS
  const [showGrid, setShowGrid] = useState(false);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [hoveredPoint, setHoveredPoint] = useState(null);

  // Scaled coordinates stored for hit-testing
  const renderedPointsRef = useRef([]);

  const inliers = tiePoints.filter((t) => t.is_inlier);
  const outliers = tiePoints.filter((t) => !t.is_inlier);
  const inlierCount = inliers.length;
  const outlierCount = outliers.length;

  useEffect(() => {
    if (!img1Src || !img2Src) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const im1 = new Image();
    const im2 = new Image();
    let loaded = 0;

    const onImageLoaded = () => {
      loaded += 1;
      if (loaded === 2) {
        draw(im1, im2);
      }
    };

    im1.onload = onImageLoaded;
    im2.onload = onImageLoaded;
    im1.src = img1Src;
    im2.src = img2Src;

    function draw(image1, image2) {
      const targetH = 460;
      const aspect1 = image1.width / image1.height;
      const aspect2 = image2.width / image2.height;

      const w1 = targetH * aspect1;
      const w2 = targetH * aspect2;
      const divider = 30;

      canvas.width = w1 + w2 + divider;
      canvas.height = targetH;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw background
      ctx.fillStyle = "#090d16";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw Image 1 (Left - Target)
      ctx.drawImage(image1, 0, 0, w1, targetH);

      // Draw Image 2 (Right - Reference)
      ctx.drawImage(image2, w1 + divider, 0, w2, targetH);

      // Draw divider separator
      ctx.fillStyle = "#1e293b";
      ctx.fillRect(w1, 0, divider, targetH);
      ctx.strokeStyle = "rgba(56, 189, 248, 0.4)";
      ctx.lineWidth = 1;
      ctx.strokeRect(w1 + 10, 0, 10, targetH);

      // Scales from original image pixels to canvas pixels
      const scaleX1 = w1 / image1.width;
      const scaleY1 = targetH / image1.height;
      const scaleX2 = w2 / image2.width;
      const scaleY2 = targetH / image2.height;

      // Draw 4x4 Spatial Validation Grid if enabled
      if (showGrid) {
        ctx.strokeStyle = "rgba(56, 189, 248, 0.45)";
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 3]);

        // 4x4 on Image 1
        for (let col = 1; col < 4; col++) {
          const gx = (w1 / 4) * col;
          ctx.beginPath();
          ctx.moveTo(gx, 0);
          ctx.lineTo(gx, targetH);
          ctx.stroke();
        }
        for (let row = 1; row < 4; row++) {
          const gy = (targetH / 4) * row;
          ctx.beginPath();
          ctx.moveTo(0, gy);
          ctx.lineTo(w1, gy);
          ctx.stroke();
        }

        // 4x4 on Image 2
        for (let col = 1; col < 4; col++) {
          const gx = w1 + divider + (w2 / 4) * col;
          ctx.beginPath();
          ctx.moveTo(gx, 0);
          ctx.lineTo(gx, targetH);
          ctx.stroke();
        }
        for (let row = 1; row < 4; row++) {
          const gy = (targetH / 4) * row;
          ctx.beginPath();
          ctx.moveTo(w1 + divider, gy);
          ctx.lineTo(w1 + divider + w2, gy);
          ctx.stroke();
        }

        // Grid Cell Annotations (Image 1)
        ctx.fillStyle = "rgba(56, 189, 248, 0.75)";
        ctx.font = "9px JetBrains Mono, monospace";
        for (let r = 0; r < 4; r++) {
          for (let c = 0; c < 4; c++) {
            ctx.fillText(
              `C[${r},${c}]`,
              (w1 / 4) * c + 5,
              (targetH / 4) * r + 14
            );
          }
        }

        ctx.setLineDash([]);
      }

      // Track point positions for interactive click hit-testing
      const pointsHitMap = [];

      // Draw Correspondence Lines & Keypoints
      tiePoints.forEach((tp) => {
        if (filterMode === "INLIERS" && !tp.is_inlier) return;
        if (filterMode === "OUTLIERS" && tp.is_inlier) return;

        const x1 = tp.pt1.x * scaleX1;
        const y1 = tp.pt1.y * scaleY1;

        const x2 = w1 + divider + tp.pt2.x * scaleX2;
        const y2 = tp.pt2.y * scaleY2;

        pointsHitMap.push({
          point: tp,
          x1,
          y1,
          x2,
          y2
        });

        const isSelected = selectedPoint && selectedPoint.id === tp.id;
        const isHovered = hoveredPoint && hoveredPoint.id === tp.id;
        const isHighlighted = isSelected || isHovered;

        // Line style
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);

        if (tp.is_inlier) {
          ctx.strokeStyle = isHighlighted ? "#38bdf8" : "rgba(34, 197, 94, 0.75)";
          ctx.lineWidth = isHighlighted ? 3.0 : 1.6;
          ctx.setLineDash([]);
        } else {
          ctx.strokeStyle = isHighlighted ? "#f87171" : "rgba(239, 68, 68, 0.4)";
          ctx.lineWidth = isHighlighted ? 2.5 : 1.2;
          ctx.setLineDash([4, 4]); // Dashed for outliers
        }
        ctx.stroke();

        // Keypoint circle 1
        ctx.beginPath();
        ctx.arc(x1, y1, isHighlighted ? 6.0 : 3.5, 0, 2 * Math.PI);
        ctx.fillStyle = tp.is_inlier ? "#22c55e" : "#ef4444";
        ctx.fill();
        if (isHighlighted) {
          ctx.strokeStyle = "#ffffff";
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }

        // Keypoint circle 2
        ctx.beginPath();
        ctx.arc(x2, y2, isHighlighted ? 6.0 : 3.5, 0, 2 * Math.PI);
        ctx.fillStyle = tp.is_inlier ? "#22c55e" : "#ef4444";
        ctx.fill();
        if (isHighlighted) {
          ctx.strokeStyle = "#ffffff";
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }

        // Label if selected
        if (isSelected) {
          ctx.fillStyle = "#ffffff";
          ctx.font = "bold 10px Inter, sans-serif";
          ctx.fillText(`Match #${tp.id}`, x1 + 8, y1 - 6);
        }
      });

      renderedPointsRef.current = pointsHitMap;
    }
  }, [img1Src, img2Src, tiePoints, filterMode, showGrid, selectedPoint, hoveredPoint]);

  // Handle canvas click for interactive tie-point inspection
  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const clickX = (e.clientX - rect.left) * scaleX;
    const clickY = (e.clientY - rect.top) * scaleY;

    // Search for closest point within 14px radius
    let found = null;
    let minDist = 14;

    for (const item of renderedPointsRef.current) {
      const d1 = Math.hypot(clickX - item.x1, clickY - item.y1);
      const d2 = Math.hypot(clickX - item.x2, clickY - item.y2);
      const dMin = Math.min(d1, d2);
      if (dMin < minDist) {
        minDist = dMin;
        found = item.point;
      }
    }

    setSelectedPoint(found);
  };

  return (
    <div style={{
      background: "var(--bg-secondary)",
      borderRadius: "0.75rem",
      padding: "1.25rem",
      border: "1px solid var(--border-color)",
      display: "flex",
      flexDirection: "column",
      gap: "0.85rem"
    }}>
      {/* Canvas Header & Toggles */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
          <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff" }}>
            Multi-Modal Tie-Point Correspondence Canvas
          </h3>
          <span className="badge badge-green">
            <CheckCircle2 size={11} /> {inlierCount} Inliers
          </span>
          <span className="badge badge-red">
            <XCircle size={11} /> {outlierCount} Outliers
          </span>
          {spatialCoveragePct !== undefined && (
            <span className="badge badge-blue">
              <Grid size={11} /> {spatialCoveragePct}% Spatial Grid
            </span>
          )}
        </div>

        {/* Filter & Grid Controls */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.45rem", flexWrap: "wrap" }}>
          <div style={{
            display: "flex",
            background: "rgba(15, 23, 42, 0.8)",
            padding: "0.2rem",
            borderRadius: "0.4rem",
            border: "1px solid var(--border-color)",
            gap: "0.2rem"
          }}>
            <button
              onClick={() => setFilterMode("ALL")}
              style={{
                fontSize: "0.7rem",
                padding: "0.25rem 0.55rem",
                borderRadius: "0.3rem",
                border: "none",
                cursor: "pointer",
                background: filterMode === "ALL" ? "var(--accent-blue)" : "transparent",
                color: filterMode === "ALL" ? "#ffffff" : "var(--text-muted)",
                fontWeight: filterMode === "ALL" ? 600 : 400
              }}
            >
              All Matches ({tiePoints.length})
            </button>
            <button
              onClick={() => setFilterMode("INLIERS")}
              style={{
                fontSize: "0.7rem",
                padding: "0.25rem 0.55rem",
                borderRadius: "0.3rem",
                border: "none",
                cursor: "pointer",
                background: filterMode === "INLIERS" ? "#22c55e" : "transparent",
                color: filterMode === "INLIERS" ? "#ffffff" : "var(--text-muted)",
                fontWeight: filterMode === "INLIERS" ? 600 : 400
              }}
            >
              Inliers Only ({inlierCount})
            </button>
            <button
              onClick={() => setFilterMode("OUTLIERS")}
              style={{
                fontSize: "0.7rem",
                padding: "0.25rem 0.55rem",
                borderRadius: "0.3rem",
                border: "none",
                cursor: "pointer",
                background: filterMode === "OUTLIERS" ? "#ef4444" : "transparent",
                color: filterMode === "OUTLIERS" ? "#ffffff" : "var(--text-muted)",
                fontWeight: filterMode === "OUTLIERS" ? 600 : 400
              }}
            >
              Outliers Only ({outlierCount})
            </button>
          </div>

          <button
            onClick={() => setShowGrid(!showGrid)}
            className="btn btn-outline"
            style={{
              fontSize: "0.72rem",
              padding: "0.3rem 0.65rem",
              background: showGrid ? "rgba(56, 189, 248, 0.15)" : "transparent",
              borderColor: showGrid ? "var(--accent-cyan)" : "var(--border-color)",
              color: showGrid ? "var(--accent-cyan)" : "var(--text-muted)"
            }}
          >
            <Grid size={12} /> {showGrid ? "Hide 4×4 Grid" : "Show 4×4 Grid"}
          </button>
        </div>
      </div>

      {/* Canvas Container with Click Listener */}
      <div style={{
        overflowX: "auto",
        borderRadius: "0.55rem",
        border: "1px solid var(--border-color)",
        background: "#090d16",
        textAlign: "center",
        position: "relative",
        cursor: "crosshair"
      }}>
        <canvas
          ref={canvasRef}
          onClick={handleCanvasClick}
          style={{ display: "block", margin: "0 auto", maxWidth: "100%", height: "auto" }}
          title="Click on any keypoint or tie-line to inspect diagnostics"
        />

        <div style={{
          position: "absolute",
          bottom: "8px",
          right: "12px",
          fontSize: "0.68rem",
          color: "rgba(255, 255, 255, 0.5)",
          display: "flex",
          alignItems: "center",
          gap: "0.3rem",
          background: "rgba(0,0,0,0.6)",
          padding: "0.2rem 0.5rem",
          borderRadius: "0.3rem",
          pointerEvents: "none"
        }}>
          <MousePointerClick size={11} /> Click points to inspect diagnostics
        </div>
      </div>

      {/* Selected Tie-Point Diagnostic Inspector */}
      {selectedPoint && (
        <div style={{
          background: "rgba(15, 23, 42, 0.95)",
          border: selectedPoint.is_inlier ? "1px solid rgba(34, 197, 94, 0.4)" : "1px solid rgba(239, 68, 68, 0.4)",
          borderRadius: "0.55rem",
          padding: "0.85rem 1rem",
          display: "flex",
          flexDirection: "column",
          gap: "0.5rem",
          boxShadow: "0 4px 12px rgba(0,0,0,0.4)"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontWeight: 700, fontSize: "0.85rem", color: "#ffffff" }}>
                Tie-Point Inspector: Match #{selectedPoint.id}
              </span>
              <span className={`badge ${selectedPoint.is_inlier ? "badge-green" : "badge-red"}`}>
                {selectedPoint.is_inlier ? "RANSAC INLIER" : "REJECTED OUTLIER"}
              </span>
            </div>
            <button
              onClick={() => setSelectedPoint(null)}
              style={{
                background: "transparent",
                border: "none",
                color: "var(--text-muted)",
                cursor: "pointer",
                padding: "2px"
              }}
            >
              <X size={15} />
            </button>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.75rem", fontSize: "0.75rem" }}>
            <div style={{ background: "rgba(0,0,0,0.25)", padding: "0.4rem 0.6rem", borderRadius: "0.35rem" }}>
              <div style={{ color: "var(--accent-cyan)", fontWeight: 600 }}>Image 1 (Target) [x, y]:</div>
              <div style={{ fontFamily: "JetBrains Mono, monospace", color: "#f8fafc", marginTop: "2px" }}>
                [{selectedPoint.pt1.x.toFixed(1)}, {selectedPoint.pt1.y.toFixed(1)}] px
              </div>
            </div>
            <div style={{ background: "rgba(0,0,0,0.25)", padding: "0.4rem 0.6rem", borderRadius: "0.35rem" }}>
              <div style={{ color: "var(--accent-amber)", fontWeight: 600 }}>Image 2 (Reference) [x, y]:</div>
              <div style={{ fontFamily: "JetBrains Mono, monospace", color: "#f8fafc", marginTop: "2px" }}>
                [{selectedPoint.pt2.x.toFixed(1)}, {selectedPoint.pt2.y.toFixed(1)}] px
              </div>
            </div>
            <div style={{ background: "rgba(0,0,0,0.25)", padding: "0.4rem 0.6rem", borderRadius: "0.35rem" }}>
              <div style={{ color: "var(--accent-purple)", fontWeight: 600 }}>Reprojection Error:</div>
              <div style={{ fontFamily: "JetBrains Mono, monospace", color: "#f8fafc", marginTop: "2px" }}>
                {selectedPoint.reprojection_error !== null && selectedPoint.reprojection_error !== undefined
                  ? `${selectedPoint.reprojection_error.toFixed(3)} px (Threshold: ≤ 3.0px)`
                  : "N/A (Pre-filter rejection)"}
              </div>
            </div>
            <div style={{ background: "rgba(0,0,0,0.25)", padding: "0.4rem 0.6rem", borderRadius: "0.35rem" }}>
              <div style={{ color: "var(--text-muted)", fontWeight: 600 }}>Status / Rejection Reason:</div>
              <div style={{ color: selectedPoint.is_inlier ? "#4ade80" : "#f87171", marginTop: "2px" }}>
                {selectedPoint.rejection_reason || (selectedPoint.is_inlier ? "Valid RANSAC inlier" : "Filtered by threshold")}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dataset Legend below canvas */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", fontSize: "0.74rem", textAlign: "center", color: "var(--text-muted)" }}>
        <div style={{ background: "rgba(0,0,0,0.2)", padding: "0.45rem", borderRadius: "0.35rem", border: "1px solid rgba(56, 189, 248, 0.15)" }}>
          <strong style={{ color: "var(--accent-cyan)" }}>Image 1 (Target):</strong> {datasetInfo?.img1_source || "Target Image"} (GSD: {datasetInfo?.img1_res_m || 0.25}m)
        </div>
        <div style={{ background: "rgba(0,0,0,0.2)", padding: "0.45rem", borderRadius: "0.35rem", border: "1px solid rgba(245, 158, 11, 0.15)" }}>
          <strong style={{ color: "var(--accent-amber)" }}>Image 2 (Reference):</strong> {datasetInfo?.img2_source || "Reference Image"} (GSD: {datasetInfo?.img2_res_m || 5.0}m)
        </div>
      </div>
    </div>
  );
}
