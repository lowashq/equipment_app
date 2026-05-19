import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { completeKeycloakLogin } from "../api/auth";
import LoadingSpinner from "../components/LoadingSpinner";
import { useAuth } from "../context/AuthContext";

export default function AuthCallback() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { completeLogin } = useAuth();
  const [error, setError] = useState("");
  const handledRef = useRef(false);

  useEffect(() => {
    if (handledRef.current) {
      return;
    }
    handledRef.current = true;

    const code = params.get("code");
    if (!code) {
      setError("Missing Keycloak authorization code.");
      return;
    }

    completeKeycloakLogin(code)
      .then((response) => {
        completeLogin(response);
      })
      .catch((err) => {
        setError(err.response?.data?.detail ?? "Could not complete Keycloak login.");
      });
  }, [completeLogin, params]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
        <div className="rounded-lg border border-line bg-white p-6 shadow-sm">
          <h1 className="text-xl font-bold text-ink">Authentication failed</h1>
          <p className="mt-2 text-sm text-red-700">{error}</p>
          <button className="btn-primary mt-5" onClick={() => navigate("/login")}>
            Back to login
          </button>
        </div>
      </div>
    );
  }

  return <LoadingSpinner label="Completing Keycloak login" />;
}
