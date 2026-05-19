import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { getEquipment } from "../../api/equipment";
import LoadingSpinner from "../../components/LoadingSpinner";
import StatusBadge from "../../components/StatusBadge";
import { EquipmentStatus } from "../../types";

const equipmentTypes = ["", "laptop", "projector", "camera", "server", "tablet", "oscilloscope"];
const statuses: Array<EquipmentStatus | ""> = [
  "",
  "available",
  "reserved",
  "borrowed",
  "serviced",
  "damaged"
];
const locations = [
  "",
  "Lab A",
  "Lab B",
  "Room 101",
  "Room 202",
  "Media Room",
  "Server Room",
  "Library",
  "Electronics Lab"
];

export default function EquipmentList() {
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [type, setType] = useState("");
  const [status, setStatus] = useState<EquipmentStatus | "">("");
  const [location, setLocation] = useState("");

  useEffect(() => {
    const timeout = window.setTimeout(() => setDebouncedSearch(search), 300);
    return () => window.clearTimeout(timeout);
  }, [search]);

  const filters = useMemo(
    () => ({ search: debouncedSearch, type, status, location }),
    [debouncedSearch, location, status, type]
  );

  const equipmentQuery = useQuery({
    queryKey: ["equipment", filters],
    queryFn: () => getEquipment(filters)
  });

  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <h1 className="text-2xl font-bold text-ink">Equipment</h1>
          <p className="mt-1 text-sm text-slate-600">
            Search inventory, inspect availability, and start a reservation.
          </p>
        </div>
      </div>

      <section className="grid gap-3 rounded-lg border border-line bg-white p-4 shadow-sm md:grid-cols-4">
        <label className="text-sm font-semibold text-slate-700">
          Search
          <input
            className="form-input mt-1"
            placeholder="Dell, camera, serial..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <label className="text-sm font-semibold text-slate-700">
          Type
          <select className="form-input mt-1" value={type} onChange={(e) => setType(e.target.value)}>
            {equipmentTypes.map((item) => (
              <option key={item || "all"} value={item}>
                {item ? item : "All types"}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-semibold text-slate-700">
          Status
          <select
            className="form-input mt-1"
            value={status}
            onChange={(e) => setStatus(e.target.value as EquipmentStatus | "")}
          >
            {statuses.map((item) => (
              <option key={item || "all"} value={item}>
                {item ? item : "All statuses"}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-semibold text-slate-700">
          Location
          <select
            className="form-input mt-1"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          >
            {locations.map((item) => (
              <option key={item || "all"} value={item}>
                {item ? item : "All locations"}
              </option>
            ))}
          </select>
        </label>
      </section>

      {equipmentQuery.isLoading && <LoadingSpinner label="Loading equipment" />}
      {equipmentQuery.isError && (
        <p className="rounded bg-red-50 px-4 py-3 text-sm text-red-700">
          Could not load equipment.
        </p>
      )}
      {!equipmentQuery.isLoading && !equipmentQuery.data?.length && (
        <div className="rounded-lg border border-dashed border-line bg-white px-4 py-10 text-center text-slate-500">
          No equipment matches these filters.
        </div>
      )}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {equipmentQuery.data?.map((item) => (
          <article
            className="rounded-lg border border-line bg-white p-4 shadow-sm transition hover:border-sky-200 hover:shadow-md"
            key={item.id}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <h2 className="truncate text-lg font-bold text-ink">{item.name}</h2>
                <p className="mt-1 text-sm capitalize text-slate-600">{item.type}</p>
              </div>
              <StatusBadge status={item.status} />
            </div>
            <dl className="mt-4 grid gap-2 text-sm text-slate-600">
              <div className="flex justify-between gap-3">
                <dt>Serial</dt>
                <dd className="font-semibold text-ink">{item.serial_number}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt>Location</dt>
                <dd className="font-semibold text-ink">{item.location ?? "Unassigned"}</dd>
              </div>
            </dl>
            <Link className="btn-primary mt-4 w-full" to={`/equipment/${item.id}`}>
              View Details
            </Link>
          </article>
        ))}
      </div>
    </div>
  );
}
