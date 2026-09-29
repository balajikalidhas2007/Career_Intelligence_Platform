"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

interface GitHubRepoEvidence {
  evidence_id: string;
  repo_name: string;
  full_name: string;
  html_url: string;
  description: string | null;
  language: string | null;
  topics: string[];
  stargazers_count: number;
  forks_count: number;
  is_new: boolean;
  created_at: string;
}

interface SyncResult {
  synced: number;
  created: number;
  updated: number;
  repos: GitHubRepoEvidence[];
}

type SyncState = "idle" | "syncing" | "done" | "error";

export default function GitHubPage() {
  const router = useRouter();
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [repos, setRepos] = useState<GitHubRepoEvidence[]>([]);
  const [syncState, setSyncState] = useState<SyncState>("idle");
  const [syncResult, setSyncResult] = useState<SyncResult | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const hasFetched = useRef(false);

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
        return fetch("http://localhost:8010/api/v1/github/evidence", {
          headers: { Authorization: `Bearer ${data.access_token}` },
        });
      })
      .then((res) => {
        if (res && res.ok) return res.json();
        return [];
      })
      .then((data) => {
        if (Array.isArray(data)) setRepos(data);
      })
      .catch(() => {
        router.push("/");
      });
  }, [router]);

  const handleSync = async () => {
    if (!accessToken) return;
    setSyncState("syncing");
    setErrorMsg("");
    setSyncResult(null);

    try {
      const res = await fetch("http://localhost:8010/api/v1/github/sync", {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Sync failed" }));
        throw new Error(err.detail || "Sync failed");
      }

      const data: SyncResult = await res.json();
      setSyncResult(data);
      setRepos(data.repos);
      setSyncState("done");
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Sync failed");
      setSyncState("error");
    }
  };

  const langColor = (lang: string | null): string => {
    const colors: Record<string, string> = {
      Python: "#3572A5",
      JavaScript: "#f1e05a",
      TypeScript: "#3178c6",
      Java: "#b07219",
      Go: "#00ADD8",
      Rust: "#dea584",
      "C++": "#f34b7d",
      C: "#555555",
      Ruby: "#701516",
      HTML: "#e34c26",
      CSS: "#563d7c",
    };
    return colors[lang || ""] || "#959da5";
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
        <h1>GitHub Repositories</h1>
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

      {/* Sync Button */}
      <div style={{ marginTop: "1.5rem" }}>
        <button
          onClick={handleSync}
          disabled={syncState === "syncing"}
          style={{
            padding: "0.75rem 1.5rem",
            backgroundColor: syncState === "syncing" ? "#9e9e9e" : "#24292e",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: syncState === "syncing" ? "wait" : "pointer",
            fontSize: "1rem",
          }}
        >
          {syncState === "syncing" ? "Syncing..." : "🔄 Sync GitHub Repos"}
        </button>
      </div>

      {/* Error */}
      {syncState === "error" && (
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

      {/* Sync Summary */}
      {syncResult && (
        <div
          style={{
            marginTop: "1rem",
            padding: "1rem",
            backgroundColor: "#e8f5e9",
            border: "1px solid #4caf50",
            borderRadius: "4px",
            color: "#2e7d32",
          }}
        >
          Synced {syncResult.synced} repos ({syncResult.created} new, {syncResult.updated} updated)
        </div>
      )}

      {/* Repos List */}
      {repos.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <h2>{repos.length} Repositories</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginTop: "1rem" }}>
            {repos.map((repo) => (
              <div
                key={repo.evidence_id}
                style={{
                  padding: "1rem",
                  border: "1px solid #e0e0e0",
                  borderRadius: "6px",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <a
                      href={repo.html_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ fontWeight: 600, color: "#1976d2", textDecoration: "none" }}
                    >
                      {repo.full_name}
                    </a>
                    {repo.is_new && (
                      <span
                        style={{
                          marginLeft: "0.5rem",
                          fontSize: "0.75rem",
                          padding: "0.1rem 0.4rem",
                          backgroundColor: "#e8f5e9",
                          color: "#2e7d32",
                          borderRadius: "4px",
                        }}
                      >
                        NEW
                      </span>
                    )}
                  </div>
                  <div style={{ display: "flex", gap: "0.75rem", fontSize: "0.85rem", color: "#666" }}>
                    {repo.stargazers_count > 0 && <span>⭐ {repo.stargazers_count}</span>}
                    {repo.forks_count > 0 && <span>🍴 {repo.forks_count}</span>}
                  </div>
                </div>

                {repo.description && (
                  <div style={{ marginTop: "0.5rem", color: "#555", fontSize: "0.9rem" }}>
                    {repo.description}
                  </div>
                )}

                <div style={{ marginTop: "0.5rem", display: "flex", flexWrap: "wrap", gap: "0.35rem", alignItems: "center" }}>
                  {repo.language && (
                    <span style={{ display: "flex", alignItems: "center", gap: "0.25rem", fontSize: "0.8rem", color: "#555" }}>
                      <span style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: langColor(repo.language), display: "inline-block" }} />
                      {repo.language}
                    </span>
                  )}
                  {repo.topics.map((topic) => (
                    <span
                      key={topic}
                      style={{
                        fontSize: "0.75rem",
                        padding: "0.1rem 0.5rem",
                        backgroundColor: "#e3f2fd",
                        color: "#1565c0",
                        borderRadius: "12px",
                        border: "1px solid #bbdefb",
                      }}
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {repos.length === 0 && syncState !== "syncing" && (
        <div style={{ marginTop: "2rem", textAlign: "center", color: "#999" }}>
          <p>No GitHub repositories synced yet.</p>
          <p>Click &quot;Sync GitHub Repos&quot; to import your repositories.</p>
        </div>
      )}
    </div>
  );
}
