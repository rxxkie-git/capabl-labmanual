import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [experiments, setExperiments] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [loadingUpload, setLoadingUpload] = useState(false);
  const [loadingGenerate, setLoadingGenerate] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const API_BASE = "http://localhost:8000";

  const handleFileChange = (e) => {
    setFile(e.target.files?.[0] || null);
    setExperiments([]);
    setSelectedId(null);
    setResult(null);
    setError("");
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }
    setLoadingUpload(true);
    setError("");
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/upload-file`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Failed to extract experiments");
      }

      const data = await res.json();
      setExperiments(data.experiments || []);
      if ((data.experiments || []).length > 0) {
        setSelectedId(data.experiments[0].id);
      }
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong");
    } finally {
      setLoadingUpload(false);
    }
  };

  const handleGenerate = async () => {
    if (selectedId === null) {
      setError("Please select an experiment.");
      return;
    }
    const selected = experiments.find((e) => e.id === selectedId);
    if (!selected) {
      setError("Invalid experiment selected.");
      return;
    }

    setLoadingGenerate(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ experiment_text: selected.text }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Failed to generate report");
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong");
    } finally {
      setLoadingGenerate(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        background: "#0f172a",
        color: "#e5e7eb",
        padding: "2rem",
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "960px",
          background: "#020617",
          borderRadius: "1.5rem",
          padding: "2rem",
          boxShadow: "0 20px 40px rgba(0,0,0,0.4)",
          border: "1px solid #1f2937",
        }}
      >
        <h1 style={{ fontSize: "1.8rem", marginBottom: "0.5rem" }}>
          AI Lab Manual Assistant
        </h1>
        <p style={{ marginBottom: "1.5rem", color: "#9ca3af" }}>
          Upload your lab manual (PDF/DOCX), pick an experiment, and get the
          procedure, theory, and safety.
        </p>

        {/* File upload */}
        <div
          style={{
            border: "1px dashed #4b5563",
            borderRadius: "1rem",
            padding: "1.5rem",
            marginBottom: "1.5rem",
          }}
        >
          <label
            style={{ display: "block", marginBottom: "0.75rem", fontWeight: 500 }}
          >
            1. Upload lab manual
          </label>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileChange}
            style={{ marginBottom: "0.75rem" }}
          />
          <div>
            <button
              onClick={handleUpload}
              disabled={loadingUpload || !file}
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "999px",
                border: "none",
                cursor: loadingUpload || !file ? "not-allowed" : "pointer",
                opacity: loadingUpload || !file ? 0.6 : 1,
                fontWeight: 500,
              }}
            >
              {loadingUpload ? "Extracting experiments..." : "Extract Experiments"}
            </button>
          </div>
        </div>

        {/* Experiments list */}
        {experiments.length > 0 && (
          <div
            style={{
              marginBottom: "1.5rem",
              padding: "1.5rem",
              borderRadius: "1rem",
              background: "#020617",
              border: "1px solid #1f2937",
            }}
          >
            <label
              style={{ display: "block", marginBottom: "0.75rem", fontWeight: 500 }}
            >
              2. Select an experiment
            </label>
            <div
              style={{
                maxHeight: "220px",
                overflowY: "auto",
                borderRadius: "0.75rem",
                border: "1px solid #111827",
              }}
            >
              {experiments.map((exp) => (
                <div
                  key={exp.id}
                  onClick={() => setSelectedId(exp.id)}
                  style={{
                    padding: "0.75rem 1rem",
                    borderBottom: "1px solid #111827",
                    background: exp.id === selectedId ? "#111827" : "#020617",
                    cursor: "pointer",
                  }}
                >
                  <div style={{ fontWeight: 500, marginBottom: "0.25rem" }}>
                    {exp.title}
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "#9ca3af" }}>
                    {exp.preview}...
                  </div>
                </div>
              ))}
            </div>
            <button
              onClick={handleGenerate}
              disabled={loadingGenerate || selectedId === null}
              style={{
                marginTop: "1rem",
                padding: "0.5rem 1.2rem",
                borderRadius: "999px",
                border: "none",
                cursor:
                  loadingGenerate || selectedId === null
                    ? "not-allowed"
                    : "pointer",
                opacity: loadingGenerate || selectedId === null ? 0.6 : 1,
                fontWeight: 500,
              }}
            >
              {loadingGenerate
                ? "Generating..."
                : "Generate Procedure, Theory & Safety"}
            </button>
          </div>
        )}

        {/* Error */}
        {error && (
          <div
            style={{
              marginBottom: "1rem",
              padding: "0.75rem 1rem",
              borderRadius: "0.75rem",
              background: "#450a0a",
              color: "#fecaca",
              fontSize: "0.9rem",
            }}
          >
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div
            style={{
              marginTop: "1rem",
              padding: "1.5rem",
              borderRadius: "1rem",
              background: "#020617",
              border: "1px solid #1f2937",
            }}
          >
            <h2 style={{ fontSize: "1.2rem", marginBottom: "1rem" }}>
              Generated Report
            </h2>
            <section style={{ marginBottom: "1rem" }}>
              <h3 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>
                Procedure
              </h3>
              <p
                style={{
                  whiteSpace: "pre-wrap",
                  fontSize: "0.95rem",
                  color: "#e5e7eb",
                }}
              >
                {result.procedure}
              </p>
            </section>
            <section style={{ marginBottom: "1rem" }}>
              <h3 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>
                Theory
              </h3>
              <p
                style={{
                  whiteSpace: "pre-wrap",
                  fontSize: "0.95rem",
                  color: "#e5e7eb",
                }}
              >
                {result.theory}
              </p>
            </section>
            <section>
              <h3 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>Safety</h3>
              <p
                style={{
                  whiteSpace: "pre-wrap",
                  fontSize: "0.95rem",
                  color: "#e5e7eb",
                }}
              >
                {result.safety}
              </p>
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
