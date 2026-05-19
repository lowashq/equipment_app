import { useQuery } from "@tanstack/react-query";

import { downloadReport, getRentalStatistics } from "../../api/reports";
import LoadingSpinner from "../../components/LoadingSpinner";

export default function Reports() {
  const statisticsQuery = useQuery({
    queryKey: ["reports", "statistics"],
    queryFn: getRentalStatistics
  });

  if (statisticsQuery.isLoading) {
    return <LoadingSpinner label="Loading reports" />;
  }

  if (!statisticsQuery.data) {
    return (
      <p className="rounded bg-red-50 px-4 py-3 text-sm text-red-700">
        Could not load statistics.
      </p>
    );
  }

  const stats = statisticsQuery.data;
  const maxStatus = Math.max(...Object.values(stats.equipment_by_status), 1);

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-bold text-ink">Reports</h1>
          <p className="mt-1 text-sm text-slate-600">
            Rental statistics, equipment health, and export files.
          </p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary" onClick={() => downloadReport("csv")}>
            Export CSV
          </button>
          <button className="btn-primary" onClick={() => downloadReport("pdf")}>
            Export PDF
          </button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Metric label="Total equipment" value={stats.total_equipment} />
        <Metric label="Active reservations" value={stats.active_reservations} />
        <Metric label="Completed" value={stats.completed_reservations} />
        <Metric label="Cancelled" value={stats.cancelled_reservations} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
          <h2 className="text-lg font-bold text-ink">Equipment by status</h2>
          <div className="mt-4 space-y-3">
            {Object.entries(stats.equipment_by_status).map(([status, count]) => (
              <div key={status}>
                <div className="flex justify-between text-sm">
                  <span className="font-semibold capitalize text-slate-700">{status}</span>
                  <span className="text-slate-500">{count}</span>
                </div>
                <div className="mt-1 h-2 rounded bg-slate-100">
                  <div
                    className="h-2 rounded bg-sky-700"
                    style={{ width: `${(count / maxStatus) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
          <h2 className="text-lg font-bold text-ink">Top rented equipment</h2>
          <table className="mt-4 min-w-full divide-y divide-line text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="py-2">Name</th>
                <th className="py-2">Type</th>
                <th className="py-2">Rentals</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {stats.most_rented_equipment.map((item) => (
                <tr key={`${item.name}-${item.type}`}>
                  <td className="py-2 font-semibold text-ink">{item.name}</td>
                  <td className="py-2 capitalize text-slate-600">{item.type}</td>
                  <td className="py-2 text-slate-600">{item.rental_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>

      <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
        <p className="text-sm font-semibold text-slate-500">Unresolved fault reports</p>
        <p className="mt-2 text-3xl font-bold text-ink">{stats.fault_reports_unresolved}</p>
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
