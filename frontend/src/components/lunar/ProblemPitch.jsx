import React from "react";

const ROWS = [
  {
    problem: "Different sensors capture the same area at totally different resolutions",
    solution: "Our system bridges sensor gaps automatically — no manual re-scaling needed",
  },
  {
    problem: "Sun angle changes make craters look completely different between images",
    solution: "Smart Feature Detection finds landmarks that stay consistent regardless of lighting",
  },
  {
    problem: "False matches in shadowed craters corrupt the alignment",
    solution: "Quality Filter removes bad matches — only reliable tie-points are kept",
  },
  {
    problem: "Match points cluster in one region, causing lopsided alignment",
    solution: "Spread-check ensures matches cover the whole image before finalising",
  },
];

export default function ProblemPitch() {
  return (
    <div className="card animate-fade-in">
      <div style={{ marginBottom: "1rem" }}>
        <h2 className="page-title">Why LunaAlign?</h2>
        <p className="page-sub">Four real problems in lunar image alignment — and how we solve each one.</p>
      </div>

      <table className="simple-table">
        <thead>
          <tr>
            <th style={{ width: "50%" }}>Problem</th>
            <th>Our Solution</th>
          </tr>
        </thead>
        <tbody>
          {ROWS.map((row, i) => (
            <tr key={i}>
              <td style={{ color: "var(--red)", lineHeight: 1.5 }}>{row.problem}</td>
              <td style={{ color: "var(--green)", lineHeight: 1.5 }}>{row.solution}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
