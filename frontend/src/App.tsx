import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleGuard from "./components/RoleGuard";
import { AuthProvider } from "./context/AuthContext";
import EquipmentManager from "./pages/Admin/EquipmentManager";
import Reports from "./pages/Admin/Reports";
import UserManager from "./pages/Admin/UserManager";
import AuthCallback from "./pages/AuthCallback";
import Dashboard from "./pages/Dashboard";
import EquipmentDetail from "./pages/Equipment/EquipmentDetail";
import EquipmentList from "./pages/Equipment/EquipmentList";
import Login from "./pages/Login";
import Notifications from "./pages/Notifications";
import Register from "./pages/Register";
import ReservationList from "./pages/Reservations/ReservationList";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      refetchOnWindowFocus: false,
      retry: 1
    }
  }
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/auth/callback" element={<AuthCallback />} />
            <Route element={<Layout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/equipment" element={<EquipmentList />} />
              <Route path="/equipment/:id" element={<EquipmentDetail />} />

              <Route element={<ProtectedRoute />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/notifications" element={<Notifications />} />
                <Route path="/reservations" element={<ReservationList />} />

                <Route element={<RoleGuard roles={["equipment_manager", "admin"]} />}>
                  <Route path="/admin/equipment" element={<EquipmentManager />} />
                  <Route path="/admin/reports" element={<Reports />} />
                </Route>
                <Route element={<RoleGuard roles={["admin"]} />}>
                  <Route path="/admin/users" element={<UserManager />} />
                </Route>
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/equipment" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
