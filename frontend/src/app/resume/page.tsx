"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

interface ExtractedSkill {
  skill_id: string;
  name: string;
  category: string | null;
  confidence: number;
  extraction_method: string | null;
}

interface ResumeResult {
  evidence_id: string;
  title: string;
  filename: string;
  text_length: number;
  skills_extracted: number;
  skills: ExtractedSkill[];
  created_at: string;
}

type UploadState = "idle" | "uploading" | "success" | "error";

export default function ResumePage() {
  const router = useRouter();
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [result, setResult] = useState<ResumeResult | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [pastResumes, setPastResumes] = useState<ResumeResult[]>([]);
  const hasFetched = useRef(false);

  // Authenticate on mount
  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;

    fetch("http://localhost:8010/api/v1/auth/refresh", {
      method: "POST",
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Not authenticated");
        return res.json();
      })
      .then((data) => {
        setAccessToken(data.access_token);
        // Load past resumes
        return fetch("http://localhost:8010/api/v1/resume/evidence", {
          headers: { Authorization: `Bearer ${data.access_token}` },
        });
      })
      .then((res) => {
        if (res && res.ok) return res.json();
        return [];
      })
      .then((data) => {
        if (Array.isArray(data)) setPastResumes(data);
      })
      .catch(() => {
        router.push("/");
      });
  }, [router]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !accessToken) return;

    setUploadState("uploading");
    setErrorMsg("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8010/api/v1/resume/upload", {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` },
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Upload failed" }));
        throw new Error(err.detail || "Upload failed");
      }

      const data: ResumeResult = await res.json();
      setResult(data);
      setUploadState("success");
      setPastResumes((prev) => [data, ...prev]);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Upload failed");
      setUploadState("error");
    }

    // Reset file input
    e.target.value = "";
  };

  const confidenceColor = (c: number) => {
    if (c >= 0.7) return "#2e7d32";
    if (c >= 0.4) return "#f57f17";
    return "#9e9e9e";
  };

  const confidenceLabel = (c: number) => {
    if (c >= 0.7) return "Strong";
    if (c >= 0.4) return "Moderate";
    return "Mentioned";
  };

  if (!accessToken) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <div>Authenticating...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "900px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Resume Analysis</h1>
        <button
          onClick={() => router.push("/dashboard")}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#1976d2",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          ← Dashboard
        </button>
      </div>

      {/* Upload Section */}
      <div
        style={{
          marginTop: "2rem",
          padding: "2rem",
          border: "2px dashed #ccc",
          borderRadius: "8px",
          textAlign: "center",
        }}
      >
        <p style={{ marginBottom: "1rem", color: "#666" }}>
          Upload your resume (PDF or DOCX) to extract skills
        </p>
        <label
          style={{
            display: "inline-block",
            padding: "0.75rem 1.5rem",
            backgroundColor: uploadState === "uploading" ? "#9e9e9e" : "#1976d2",
            color: "white",
            borderRadius: "4px",
            cursor: uploadState === "uploading" ? "wait" : "pointer",
          }}
        >
          {uploadState === "uploading" ? "Processing..." : "Choose File"}
          <input
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={handleUpload}
            disabled={uploadState === "uploading"}
            style={{ display: "none" }}
          />
        </label>
      </div>

      {/* Error */}
      {uploadState === "error" && (
        <div
          style={{
            marginTop: "1rem",
            padding: "1rem",
            backgroundColor: "#ffebee",
            border: "1px solid #f44336",
            borderRadius: "4px",
            color: "#c62828",
          }}
        >
          {errorMsg}
        </div>
      )}

      {/* Result */}
      {result && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Extracted Skills from: {result.filename}</h2>
          <p style={{ color: "#666" }}>
            {result.text_length.toLocaleString()} characters extracted •{" "}
            {result.skills_extracted} skills identified
          </p>

          <div
            style={{
              marginTop: "1rem",
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
              gap: "0.75rem",
            }}
          >
            {result.skills
              .sort((a, b) => b.confidence - a.confidence)
              .map((skill) => (
                <div
                  key={skill.skill_id}
                  style={{
                    padding: "0.75rem",
                    border: "1px solid #e0e0e0",
                    borderRadius: "6px",
                    borderLeft: `4px solid ${confidenceColor(skill.confidence)}`,
                  }}
                >
                  <div style={{ fontWeight: 600 }}>{skill.name}</div>
                  <div style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.25rem" }}>
                    {skill.category && <span>{skill.category.replace("_", " ")} • </span>}
                    <span style={{ color: confidenceColor(skill.confidence) }}>
                      {confidenceLabel(skill.confidence)} ({Math.round(skill.confidence * 100)}%)
                    </span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Past Resumes */}
      {pastResumes.length > 0 && !result && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Previous Resume Analyses</h2>
          {pastResumes.map((resume) => (
            <div
              key={resume.evidence_id}
              style={{
                marginTop: "1rem",
                padding: "1rem",
                border: "1px solid #e0e0e0",
                borderRadius: "6px",
              }}
            >
              <div style={{ fontWeight: 600 }}>{resume.title}</div>
              <div style={{ fontSize: "0.85rem", color: "#666" }}>
                {resume.skills_extracted} skills •{" "}
                {new Date(resume.created_at).toLocaleDateString()}
              </div>
              <div style={{ marginTop: "0.5rem", display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                {resume.skills
                  .sort((a, b) => b.confidence - a.confidence)
                  .slice(0, 10)
                  .map((s) => (
                    <span
                      key={s.skill_id}
                      style={{
                        fontSize: "0.8rem",
                        padding: "0.15rem 0.5rem",
                        backgroundColor: "#f5f5f5",
                        borderRadius: "12px",
                        border: "1px solid #e0e0e0",
                      }}
                    >
                      {s.name}
                    </span>
                  ))}
                {resume.skills_extracted > 10 && (
                  <span style={{ fontSize: "0.8rem", color: "#999", padding: "0.15rem 0.5rem" }}>
                    +{resume.skills_extracted - 10} more
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
