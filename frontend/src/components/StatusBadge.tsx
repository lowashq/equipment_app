const statusStyles: Record<string, string> = {
  available: "bg-green-100 text-green-800 border-green-200",
  reserved: "bg-yellow-100 text-yellow-800 border-yellow-200",
  borrowed: "bg-blue-100 text-blue-800 border-blue-200",
  serviced: "bg-orange-100 text-orange-800 border-orange-200",
  damaged: "bg-red-100 text-red-800 border-red-200",
  pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
  active: "bg-blue-100 text-blue-800 border-blue-200",
  completed: "bg-green-100 text-green-800 border-green-200",
  cancelled: "bg-slate-100 text-slate-700 border-slate-200"
};

export default function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-flex rounded border px-2 py-1 text-xs font-semibold capitalize ${
        statusStyles[status] ?? "border-slate-200 bg-slate-100 text-slate-700"
      }`}
    >
      {status}
    </span>
  );
}
