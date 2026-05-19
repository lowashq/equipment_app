import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  approveReservation,
  cancelReservation,
  getReservations
} from "../../api/reservations";
import { registerReturn } from "../../api/returns";
import LoadingSpinner from "../../components/LoadingSpinner";
import StatusBadge from "../../components/StatusBadge";
import { useAuth } from "../../context/AuthContext";
import { Reservation } from "../../types";
import ReturnForm from "../Returns/ReturnForm";

export default function ReservationList() {
  const { isRole } = useAuth();
  const queryClient = useQueryClient();
  const [returnReservation, setReturnReservation] = useState<Reservation | null>(null);
  const [error, setError] = useState("");

  const reservationsQuery = useQuery({
    queryKey: ["reservations"],
    queryFn: () => getReservations()
  });

  const cancelMutation = useMutation({
    mutationFn: cancelReservation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reservations"] });
      queryClient.invalidateQueries({ queryKey: ["equipment"] });
    },
    onError: (err: any) => setError(err.response?.data?.detail ?? "Could not cancel reservation.")
  });

  const returnMutation = useMutation({
    mutationFn: registerReturn,
    onSuccess: () => {
      setReturnReservation(null);
      queryClient.invalidateQueries({ queryKey: ["reservations"] });
      queryClient.invalidateQueries({ queryKey: ["equipment"] });
    },
    onError: (err: any) => setError(err.response?.data?.detail ?? "Could not register return.")
  });

  const approveMutation = useMutation({
    mutationFn: approveReservation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reservations"] });
      queryClient.invalidateQueries({ queryKey: ["equipment"] });
    },
    onError: (err: any) => setError(err.response?.data?.detail ?? "Could not approve reservation.")
  });

  if (reservationsQuery.isLoading) {
    return <LoadingSpinner label="Loading reservations" />;
  }

  const reservations = reservationsQuery.data ?? [];

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-ink">Reservations</h1>
        <p className="mt-1 text-sm text-slate-600">
          Track rentals, cancel pending reservations, and register returns.
        </p>
      </div>

      {error && <p className="rounded bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

      <section className="rounded-lg border border-line bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-line text-sm">
            <thead className="bg-panel text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Equipment</th>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Start</th>
                <th className="px-4 py-3">End</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {reservations.map((reservation) => (
                <tr key={reservation.id}>
                  <td className="px-4 py-3">
                    <p className="font-semibold text-ink">{reservation.equipment.name}</p>
                    <p className="text-xs text-slate-500">{reservation.equipment.serial_number}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{reservation.user.email}</td>
                  <td className="px-4 py-3 text-slate-600">{reservation.start_date}</td>
                  <td className="px-4 py-3 text-slate-600">{reservation.end_date}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={reservation.status} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      {reservation.status === "pending" && (
                        <button
                          className="btn-secondary"
                          onClick={() => cancelMutation.mutate(reservation.id)}
                        >
                          Cancel
                        </button>
                      )}
                      {reservation.status === "pending" &&
                        isRole("staff", "equipment_manager", "admin") && (
                          <button
                            className="btn-primary"
                            onClick={() => approveMutation.mutate(reservation.id)}
                          >
                            Approve
                          </button>
                        )}
                      {(reservation.status === "active" || reservation.status === "pending") && (
                        <button
                          className="btn-primary"
                          onClick={() => setReturnReservation(reservation)}
                        >
                          Return
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {!reservations.length && (
                <tr>
                  <td className="px-4 py-8 text-center text-slate-500" colSpan={6}>
                    No reservations found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {returnReservation && (
        <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
          <h2 className="text-lg font-bold text-ink">
            Return {returnReservation.equipment.name}
          </h2>
          <div className="mt-4">
            <ReturnForm
              reservationId={returnReservation.id}
              isSubmitting={returnMutation.isPending}
              onCancel={() => setReturnReservation(null)}
              onSubmit={(payload) => returnMutation.mutate(payload)}
            />
          </div>
        </section>
      )}
    </div>
  );
}
