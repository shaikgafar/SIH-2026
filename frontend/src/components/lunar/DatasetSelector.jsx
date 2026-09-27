import React, { useState } from "react";
import { CheckCircle2, Upload, ZoomIn, Sun, Layers } from "lucide-react";

function challengeChip(type) {
  switch (type) {
    case "SCALE_INVARIANCE":
      return <span className="chip chip-blue"><ZoomIn size={11} /> Scale</span>;
    case "SUN_ANGLE_INVARIANCE":
      return <span className="chip chip-amber"><Sun size={11} /> Lighting</span>;
    default:
      return <span className="chip chip-blue"><Layers size={11} /> Multi-sensor</span>;
  }
}

function specLine(d) {
  const a = d.img1_source || "Image A";
  const b = d.img2_source || "Image B";
  const ra = d.img1_res_m ? `${d.img1_res_m} m/px` : "—";
  const rb = d.img2_res_m ? `${d.img2_res_m} m/px` : "—";
  return `${a} (${ra})  vs  ${b} (${rb})`;
}

export default function DatasetSelector({ datasets, selectedId, onSelectDataset, onCustomUpload, loading }) {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [showUpload, setShowUpload] = useState(false);

  const primaryDatasets   = datasets.filter((d) => d.category === "PRIMARY_CHANDRAYAAN" || !d.category);
  const referenceDatasets = datasets.filter((d) => d.category === "REFERENCE_VALIDATION");

  const handleFileChange = (e, idx) => {
    const f = e.target.files[0];
    if (!f) return;
    idx === 1 ? setFile1(f) : setFile2(f);
  };

  const handleUploadSubmit = (e) => {
    e.preventDefault();
    if (file1 && file2) onCustomUpload(file1, file2);
  };

  const DatasetCard = ({ d }) => {
    const active = selectedId === d.id;
    return (
      <div
        onClick={() => onSelectDataset(d.id)}
        className="card-sm"
        style={{
          border: active ? "2px solid var(--accent)" : "1px solid var(--border)",
          borderRadius: "var(--radius)",
          background: active ? "var(--bg-inner)" : "var(--bg-card)",
          cursor: "pointer",
          transition: "all 0.15s",
        }}
      >
        {/* Card header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
          <span style={{ fontSize: "0.88rem", fontWeight: 700, color: "var(--text)" }}>
            {d.title?.split(":")[0] || d.id}
          </span>
          {active
            ? <span className="chip chip-green"><CheckCircle2 size={11} /> Active</span>
            : challengeChip(d.challenge_type)
          }
        </div>

        {/* Description */}
        <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", lineHeight: 1.5, margin: "0 0 0.5rem" }}>
          {d.description}
        </p>

        {/* Spec summary */}
        <span style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontFamily: "monospace" }}>
          {specLine(d)}
        </span>
      </div>
    );
  };

  const SectionLabel = ({ label, sublabel }) => (
    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.6rem" }}>
      <span className="badge badge-blue">{label}</span>
      <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{sublabel}</span>
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 className="page-title">Select a Dataset</h2>
          <p className="page-sub">Choose a verified image pair to run alignment on.</p>
        </div>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="btn btn-outline btn-sm"
          style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}
        >
          <Upload size={13} /> {showUpload ? "Hide Uploader" : "Upload Your Own"}
        </button>
      </div>

      {/* Primary datasets */}
      <div>
        <SectionLabel label="Chandrayaan-2" sublabel="OHRC · TMC-2 · IIRS" />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px,1fr))", gap: "0.85rem" }}>
          {primaryDatasets.map((d) => <DatasetCard key={d.id} d={d} />)}
        </div>
      </div>

      {/* Reference datasets */}
      {referenceDatasets.length > 0 && (
        <div>
          <SectionLabel label="Reference / Validation" sublabel="NASA LRO · JAXA SELENE" />
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px,1fr))", gap: "0.85rem" }}>
            {referenceDatasets.map((d) => <DatasetCard key={d.id} d={d} />)}
          </div>
        </div>
      )}

      {/* Custom upload */}
      {showUpload && (
        <form onSubmit={handleUploadSubmit} className="card animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div>
            <h3 className="page-title">Upload a Custom Image Pair</h3>
            <p className="page-sub">Supported formats: PNG, JPG, TIFF. Two images required.</p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <div>
              <label className="label">Target Image (A)</label>
              <input type="file" accept=".png,.jpg,.jpeg,.tif,.tiff" onChange={(e) => handleFileChange(e, 1)} className="form-input" />
              {file1 && <p className="page-sub" style={{ marginTop: "0.3rem" }}>{file1.name} ({(file1.size / 1024).toFixed(1)} KB)</p>}
            </div>
            <div>
              <label className="label">Reference Image (B)</label>
              <input type="file" accept=".png,.jpg,.jpeg,.tif,.tiff" onChange={(e) => handleFileChange(e, 2)} className="form-input" />
              {file2 && <p className="page-sub" style={{ marginTop: "0.3rem" }}>{file2.name} ({(file2.size / 1024).toFixed(1)} KB)</p>}
            </div>
          </div>

          <button type="submit" disabled={loading || !file1 || !file2} className="btn btn-primary" style={{ width: "fit-content" }}>
            <Upload size={14} /> {loading ? "Running..." : "Run Alignment"}
          </button>
        </form>
      )}
    </div>
  );
}
