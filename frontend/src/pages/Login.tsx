import { getKeycloakLoginUrl, getKeycloakRegisterUrl } from "../api/auth";

export default function Login() {
  async function redirectToKeycloak(mode: "login" | "register") {
    const url = mode === "login" ? await getKeycloakLoginUrl() : await getKeycloakRegisterUrl();
    window.location.href = url;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <div className="w-full max-w-md rounded-lg border border-line bg-white p-6 shadow-sm">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-ink">University Equipment Rental</h1>
          <p className="mt-1 text-sm text-slate-600">
            Use your @student.san.edu.pl or @san.edu.pl account.
          </p>
        </div>

        <div className="grid gap-2">
          <button className="btn-secondary w-full" onClick={() => redirectToKeycloak("login")}>
            Login with Keycloak
          </button>
          <button className="btn-secondary w-full" onClick={() => redirectToKeycloak("register")}>
            Register with Keycloak
          </button>
        </div>
      </div>
    </div>
  );
}
