import { useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getEquipment } from "../../api/equipment";
import { getFaultReports, resolveFaultReport } from "../../api/faultReports";
import LoadingSpinner from "../../components/LoadingSpinner";

function formatDate(value?: string | null) {
  if (!value) {
    return "Unresolved";
  }

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

export default function FaultReports() {
  const queryClient = useQueryClient();

  const reportsQuery = useQuery({
    queryKey: ["fault-reports"],
    queryFn: () => getFaultReports()
  });

  const equipmentQuery = useQuery({
    queryKey: ["equipment"],
    queryFn: () => getEquipment()
  });

  const resolveMutation = useMutation({
    mutationFn: resolveFaultReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fault-reports"] });
      queryClient.invalidateQueries({ queryKey: ["equipment"] });
      queryClient.invalidateQueries({ queryKey: ["reports", "statistics"] });
    }
  });

  const equipmentById = useMemo(() => {
    return new Map((equipmentQuery.data ?? []).map((item) => [item.id, item]));
  }, [equipmentQuery.data]);

  if (reportsQuery.isLoading || equipmentQuery.isLoading) {
    return <LoadingSpinner label="Loading fault reports" />;
  }

  const reports = reportsQuery.data ?? [];
  const unresolvedCount = reports.filter((report) => !report.resolved_at).length;

  return (
    <section className="space-y-5">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <h1 className="text-2xl font-bold text-ink">Fault Reports</h1>
          <p className="mt-1 text-sm text-slate-600">
            Review equipment issues reported by users.
          </p>
        </div>
        <div className="rounded border border-line bg-white px-4 py-3 text-sm">
          <span className="font-semibold text-slate-500">Unresolved</span>
          <span className="ml-3 text-xl font-bold text-ink">{unresolvedCount}</span>
        </div>
      </div>

      <div className="overflow-hidden rounded border border-line bg-white">
        <table className="min-w-full divide-y divide-line text-sm">
          <thead className="bg-slate-50 text-left text-xs font-bold uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Equipment</th>
              <th className="px-4 py-3">Description</th>
              <th className="px-4 py-3">Reported</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {reports.map((report) => {
              const equipment = equipmentById.get(report.equipment_id);
              const resolved = Boolean(report.resolved_at);

              return (
                <tr key={report.id} className={resolved ? "bg-white" : "bg-red-50/30"}>
                  <td className="px-4 py-3 align-top">
                    <p className="font-semibold text-ink">
                      {equipment?.name ?? "Unknown equipment"}
                    </p>
                    <p className="text-xs text-slate-500">
                      {equipment
                        ? `${equipment.type} - ${equipment.serial_number}`
                        : report.equipment_id}
                    </p>
                  </td>
                  <td className="max-w-xl whitespace-pre-wrap px-4 py-3 align-top text-slate-700">
                    {report.description}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 align-top text-slate-600">
                    {formatDate(report.created_at)}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 align-top">
                    <span
                      className={`inline-flex rounded px-2 py-1 text-xs font-bold ${
                        resolved
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {resolved ? `Resolved ${formatDate(report.resolved_at)}` : "Unresolved"}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 align-top">
                    <button
                      className="btn-secondary"
                      disabled={resolved || resolveMutation.isPending}
                      onClick={() => resolveMutation.mutate(report.id)}
                    >
                      Resolve
                    </button>
                  </td>
                </tr>
              );
            })}

            {!reports.length && (
              <tr>
                <td className="px-4 py-8 text-center text-slate-500" colSpan={5}>
                  No fault reports yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
