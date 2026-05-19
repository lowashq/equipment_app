import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { getEquipment } from "../api/equipment";
import { getReservations } from "../api/reservations";
import LoadingSpinner from "../components/LoadingSpinner";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user } = useAuth();
  const reservationsQuery = useQuery({
    queryKey: ["reservations"],
    queryFn: () => getReservations()
  });
  const availableEquipmentQuery = useQuery({
    queryKey: ["equipment", { status: "available" }],
    queryFn: () => getEquipment({ status: "available" })
  });

  if (reservationsQuery.isLoading || availableEquipmentQuery.isLoading) {
    return <LoadingSpinner label="Loading dashboard" />;
  }

  const reservations = reservationsQuery.data ?? [];
  const activeCount = reservations.filter((item) => item.status === "active").length;
  const pendingCount = reservations.filter((item) => item.status === "pending").length;
  const lastReservations = reservations.slice(0, 5);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-ink">Welcome, {user?.full_name}</h1>
        <p className="mt-1 text-sm text-slate-600">
          Role: <span className="font-semibold capitalize">{user?.role}</span>
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Active reservations" value={activeCount} />
        <Metric label="Pending reservations" value={pendingCount} />
        <Metric label="Available equipment" value={availableEquipmentQuery.data?.length ?? 0} />
      </div>

      <section className="rounded-lg border border-line bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <h2 className="text-lg font-bold text-ink">Recent reservations</h2>
          <Link className="btn-secondary" to="/reservations">
            View all
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-line text-sm">
            <thead className="bg-panel text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Equipment</th>
                <th className="px-4 py-3">Dates</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {lastReservations.map((reservation) => (
                <tr key={reservation.id}>
                  <td className="px-4 py-3 font-semibold text-ink">
                    {reservation.equipment.name}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {reservation.start_date} to {reservation.end_date}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={reservation.status} />
                  </td>
                </tr>
              ))}
              {!lastReservations.length && (
                <tr>
                  <td className="px-4 py-8 text-center text-slate-500" colSpan={3}>
                    No reservations yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-line bg-white p-4 shadow-sm">
      <p className="text-sm font-semibold text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-bold text-ink">{value}</p>
    </div>
  );
}
