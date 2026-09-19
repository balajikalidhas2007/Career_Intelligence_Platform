"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  useEffect(() => {
    // Attempt to exchange the HttpOnly refresh cookie for a short-lived access token
    fetch("http://localhost:8000/api/v1/auth/refresh", {
      method: "POST",
      credentials: "include", // Essential for sending the HttpOnly cookie
    })
      .then((res) => {
        if (!res.ok) throw new Error("Not authenticated");
        return res.json();
      })
      .then((data) => {
        setAccessToken(data.access_token);
        
        // Now fetch user data using the new in-memory access token
        return fetch("http://localhost:8000/api/v1/auth/me", {
          headers: {
            Authorization: `Bearer ${data.access_token}`
          }
        });
      })
      .then((res) => {
        if (!res) return;
        if (!res.ok) throw new Error("Failed to fetch user");
        return res.json();
      })
      .then((userData) => {
        if (userData) {
          setUser(userData);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error(err);
        router.push("/");
      });
  }, [router]);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <div>Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <h1>Dashboard</h1>
      
      <div style={{ 
        marginTop: "2rem", 
        padding: "1.5rem", 
        border: "1px solid #eaeaea", 
        borderRadius: "8px",
        display: "flex",
        alignItems: "center",
        gap: "1rem"
      }}>
        {user?.avatar_url && (
          <img 
            src={user.avatar_url} 
            alt="Avatar" 
            style={{ width: "64px", height: "64px", borderRadius: "50%" }} 
          />
        )}
        <div>
          <h2>Welcome, {user?.display_name || "User"}!</h2>
          {user?.email && <p style={{ color: "#666" }}>{user.email}</p>}
        </div>
      </div>

      <div style={{ marginTop: "2rem" }}>
        <button 
          onClick={() => {
            fetch("http://localhost:8000/api/v1/auth/logout", { 
              method: "POST",
              credentials: "include",
            })
              .finally(() => {
                setAccessToken(null);
                router.push("/");
              });
          }}
          style={{ 
            padding: "0.5rem 1rem", 
            backgroundColor: "#f44336", 
            color: "white", 
            border: "none", 
            borderRadius: "4px",
            cursor: "pointer"
          }}
        >
          Sign Out
        </button>
      </div>
    </div>
  );
}
