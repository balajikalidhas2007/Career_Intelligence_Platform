"use client";

import { useEffect, Suspense } from "react";
import { useRouter } from "next/navigation";

function SuccessHandler() {
  const router = useRouter();

  useEffect(() => {
    // The backend has already set the HttpOnly refresh token cookie.
    // We just redirect to the dashboard, which will exchange it for an access token.
    router.push("/dashboard");
  }, [router]);

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
      <div style={{ textAlign: "center" }}>
        <h2>Login Successful!</h2>
        <p>Redirecting to your dashboard...</p>
      </div>
    </div>
  );
}

export default function AuthSuccessPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <SuccessHandler />
    </Suspense>
  );
}
