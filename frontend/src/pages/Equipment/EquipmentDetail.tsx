import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { useForm } from "react-hook-form";
import { Link, useParams } from "react-router-dom";

import { createFaultReport } from "../../api/faultReports";
import {
  getEquipmentById,
  getEquipmentHistory
} from "../../api/equipment";
import { createReservation } from "../../api/reservations";
import LoadingSpinner from "../../components/LoadingSpinner";
import StatusBadge from "../../components/StatusBadge";
import { useAuth } from "../../context/AuthContext";
import { ApiErrorDetail, Reservation } from "../../types";

interface ReservationForm {
  start_date: string;
  end_date: string;
}

interface FaultForm {
  description: string;
}

export default function EquipmentDetail() {
  const { id } = useParams();
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [reserveOpen, setReserveOpen] = useState(false);
  const [faultOpen, setFaultOpen] = useState(false);
  const [reservationError, setReservationError] = useState<ApiErrorDetail | null>(null);
  const [reservationMessage, setReservationMessage] = useState("");
  const [faultSuccess, setFaultSuccess] = useState("");

  const reservationForm = useForm<ReservationForm>();
  const faultForm = useForm<FaultForm>();

  const equipmentQuery = useQuery({
    queryKey: ["equipment", id],
    queryFn: () => getEquipmentById(id!),
    enabled: Boolean(id)
  });

  const historyQuery = useQuery({
    queryKey: ["equipment-history", id],
    queryFn: () => getEquipmentHistory(id!),
    enabled: Boolean(id && token)
  });

  const reserveMutation = useMutation({
    mutationFn: (values: ReservationForm) =>
      createReservation({ equipment_id: id!, ...values }),
    onSuccess: (reservation: Reservation) => {
      setReserveOpen(false);
      setReservationError(null);
      setReservationMessage(
        reservation.status === "active"
          ? "Reservation approved automatically. Your rental is active."
          : "Reservation is waiting for staff approval. Please contact staff to confirm pickup."
      );
      reservationForm.reset();
      queryClient.invalidateQueries({ queryKey: ["equipment", id] });
      queryClient.invalidateQueries({ queryKey: ["reservations"] });
    },
    onError: (error: AxiosError<ApiErrorDetail>) => {
      setReservationError(error.response?.data ?? { detail: "Could not create reservation." });
      setReservationMessage("");
    }
  });

  const faultMutation = useMutation({
    mutationFn: (values: FaultForm) =>
      createFaultReport({ equipment_id: id!, description: values.description }),
    onSuccess: () => {
      setFaultSuccess("Fault report submitted.");
      faultForm.reset();
    }
  });

  if (equipmentQuery.isLoading) {
    return <LoadingSpinner label="Loading equipment details" />;
  }

  if (!equipmentQuery.data) {
    return (
      <div className="rounded-lg border border-line bg-white p-6">
        <p className="text-sm text-slate-600">Equipment not found.</p>
        <Link className="btn-secondary mt-4" to="/equipment">
          Back to equipment
        </Link>
      </div>
    );
  }

  const equipment = equipmentQuery.data;
  const canReserve = equipment.status === "available" && Boolean(token);

  return (
    <div className="space-y-5">
      <Link className="text-sm font-semibold text-sky-700 hover:text-sky-900" to="/equipment">
        Back to equipment
      </Link>

      <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
          <div>
            <h1 className="text-2xl font-bold text-ink">{equipment.name}</h1>
            <p className="mt-1 text-sm capitalize text-slate-600">{equipment.type}</p>
          </div>
          <StatusBadge status={equipment.status} />
        </div>

        <dl className="mt-5 grid gap-4 md:grid-cols-2">
          <Info label="Serial number" value={equipment.serial_number} />
          <Info label="Location" value={equipment.location ?? "Unassigned"} />
          <Info label="Max rental days" value={`${equipment.max_rental_days}`} />
          <Info label="Created" value={new Date(equipment.created_at).toLocaleString()} />
          <div className="md:col-span-2">
            <Info label="Technical spec" value={equipment.technical_spec ?? "No specs provided"} />
          </div>
        </dl>

        <div className="mt-6 flex flex-wrap gap-3">
          {token ? (
            <>
              <button
                className="btn-primary"
                disabled={!canReserve}
                onClick={() => setReserveOpen(true)}
              >
                Reserve
              </button>
              <button className="btn-secondary" onClick={() => setFaultOpen((value) => !value)}>
                Report Fault
              </button>
            </>
          ) : (
            <Link className="btn-primary" to="/login">
              Login to reserve
            </Link>
          )}
        </div>
      </section>

      {reserveOpen && (
        <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
          <h2 className="text-lg font-bold text-ink">Reserve equipment</h2>
          <form
            className="mt-4 grid gap-4 md:grid-cols-[1fr_1fr_auto]"
            onSubmit={reservationForm.handleSubmit((values) => reserveMutation.mutate(values))}
          >
            <label className="text-sm font-semibold text-slate-700">
              Start date
              <input
                className="form-input mt-1"
                type="date"
                {...reservationForm.register("start_date", { required: true })}
              />
            </label>
            <label className="text-sm font-semibold text-slate-700">
              End date
              <input
                className="form-input mt-1"
                type="date"
                {...reservationForm.register("end_date", { required: true })}
              />
            </label>
            <div className="flex items-end gap-2">
              <button className="btn-primary" disabled={reserveMutation.isPending}>
                Submit
              </button>
              <button className="btn-secondary" type="button" onClick={() => setReserveOpen(false)}>
                Cancel
              </button>
            </div>
          </form>
          {reservationError && (
            <div className="mt-4 rounded bg-red-50 px-4 py-3 text-sm text-red-700">
              <p className="font-semibold">{reservationError.detail ?? "Reservation rejected."}</p>
              {reservationError.reasons?.length ? (
                <ul className="mt-2 list-disc pl-5">
                  {reservationError.reasons.map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>
              ) : null}
            </div>
          )}
        </section>
      )}

      {reservationMessage && (
        <div className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-sm font-semibold text-sky-900">
          {reservationMessage}
        </div>
      )}

      {faultOpen && (
        <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
          <h2 className="text-lg font-bold text-ink">Report fault</h2>
          <form
            className="mt-4 space-y-3"
            onSubmit={faultForm.handleSubmit((values) => faultMutation.mutate(values))}
          >
            <textarea
              className="form-input min-h-28"
              placeholder="Describe the issue"
              {...faultForm.register("description", { required: true })}
            />
            <button className="btn-primary" disabled={faultMutation.isPending}>
              Submit report
            </button>
          </form>
          {faultSuccess && <p className="mt-3 text-sm font-semibold text-green-700">{faultSuccess}</p>}
        </section>
      )}

      <section className="rounded-lg border border-line bg-white shadow-sm">
        <div className="border-b border-line px-4 py-3">
          <h2 className="text-lg font-bold text-ink">Rental history</h2>
        </div>
        {!token && (
          <p className="px-4 py-6 text-sm text-slate-600">Login to view rental history.</p>
        )}
        {token && historyQuery.isLoading && <LoadingSpinner label="Loading history" />}
        {token && !historyQuery.data?.length && !historyQuery.isLoading && (
          <p className="px-4 py-6 text-sm text-slate-600">No rental history yet.</p>
        )}
        {Boolean(historyQuery.data?.length) && (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-line text-sm">
              <thead className="bg-panel text-left text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-3">User</th>
                  <th className="px-4 py-3">Dates</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Return</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {historyQuery.data?.map((item) => (
                  <tr key={item.id}>
                    <td className="px-4 py-3">
                      <p className="font-semibold text-ink">{item.user.full_name}</p>
                      <p className="text-xs text-slate-500">{item.user.email}</p>
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {item.start_date} to {item.end_date}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {item.return_info
                        ? `${item.return_info.condition}: ${item.return_info.notes ?? ""}`
                        : "No return record"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-bold uppercase text-slate-400">{label}</dt>
      <dd className="mt-1 text-sm font-semibold text-ink">{value}</dd>
    </div>
  );
}
