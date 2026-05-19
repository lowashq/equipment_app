import api from "./client";
import { Reservation, ReservationStatus } from "../types";

export interface ReservationPayload {
  equipment_id: string;
  start_date: string;
  end_date: string;
}

export async function getReservations(status?: ReservationStatus | ""): Promise<Reservation[]> {
  const { data } = await api.get<Reservation[]>("/reservations", {
    params: status ? { status } : undefined
  });
  return data;
}

export async function createReservation(payload: ReservationPayload): Promise<Reservation> {
  const { data } = await api.post<Reservation>("/reservations", payload);
  return data;
}

export async function cancelReservation(id: string): Promise<void> {
  await api.delete(`/reservations/${id}`);
}

export async function approveReservation(id: string): Promise<Reservation> {
  const { data } = await api.patch<Reservation>(`/reservations/${id}/approve`);
  return data;
}
