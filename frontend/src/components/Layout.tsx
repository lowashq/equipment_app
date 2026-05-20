import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const navLinkBase =
  "block rounded px-3 py-2 text-sm font-semibold transition hover:bg-slate-100";

export default function Layout() {
  const { user, logout, isRole } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-100">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-white px-4 py-5 md:block">
        <button
          className="mb-6 text-left text-lg font-bold text-ink"
          onClick={() => navigate("/dashboard")}
        >
          Equipment Rental
        </button>
        <nav className="space-y-1">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `${navLinkBase} ${isActive ? "bg-sky-50 text-sky-800" : "text-slate-700"}`
            }
          >
            Dashboard
          </NavLink>
          <NavLink
            to="/equipment"
            className={({ isActive }) =>
              `${navLinkBase} ${isActive ? "bg-sky-50 text-sky-800" : "text-slate-700"}`
            }
          >
            Equipment
          </NavLink>
          <NavLink
            to="/reservations"
            className={({ isActive }) =>
              `${navLinkBase} ${isActive ? "bg-sky-50 text-sky-800" : "text-slate-700"}`
            }
          >
            Reservations
          </NavLink>
          <NavLink
            to="/notifications"
            className={({ isActive }) =>
              `${navLinkBase} ${isActive ? "bg-sky-50 text-sky-800" : "text-slate-700"}`
            }
          >
            Notifications
          </NavLink>
          {isRole("equipment_manager", "admin") && (
            <>
              <div className="px-3 pt-5 text-xs font-bold uppercase tracking-wide text-slate-400">
                Admin
              </div>
              <NavLink
                to="/admin/equipment"
                className={({ isActive }) =>
                  `${navLinkBase} ${
                    isActive ? "bg-sky-50 text-sky-800" : "text-slate-700"
                  }`
                }
              >
                Equipment Manager
              </NavLink>
              <NavLink
                to="/admin/reports"
                className={({ isActive }) =>
                  `${navLinkBase} ${
                    isActive ? "bg-sky-50 text-sky-800" : "text-slate-700"
                  }`
                }
              >
                Reports
              </NavLink>
              <NavLink
                to="/admin/fault-reports"
                className={({ isActive }) =>
                  `${navLinkBase} ${
                    isActive ? "bg-sky-50 text-sky-800" : "text-slate-700"
                  }`
                }
              >
                Fault Reports
              </NavLink>
              {isRole("admin") && (
                <NavLink
                  to="/admin/users"
                  className={({ isActive }) =>
                    `${navLinkBase} ${
                      isActive ? "bg-sky-50 text-sky-800" : "text-slate-700"
                    }`
                  }
                >
                  Users
                </NavLink>
              )}
            </>
          )}
        </nav>
      </aside>

      <div className="md:pl-64">
        <header className="sticky top-0 z-20 border-b border-line bg-white/95 px-4 py-3 backdrop-blur">
          <div className="flex items-center justify-between gap-4">
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-ink">
                {user?.full_name ?? "Guest"}
              </p>
              <p className="text-xs capitalize text-slate-500">{user?.role ?? "public"}</p>
            </div>
            <div className="flex items-center gap-2">
              <NavLink className="btn-secondary md:hidden" to="/equipment">
                Equipment
              </NavLink>
              {user ? (
                <button className="btn-secondary" onClick={logout}>
                  Logout
                </button>
              ) : (
                <button className="btn-primary" onClick={() => navigate("/login")}>
                  Login
                </button>
              )}
            </div>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
