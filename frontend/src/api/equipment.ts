import api from "./client";
import { Equipment, EquipmentHistoryItem, EquipmentStatus } from "../types";

export interface EquipmentFilters {
  search?: string;
  type?: string;
  status?: EquipmentStatus | "";
  location?: string;
}

export interface EquipmentPayload {
  name: string;
  type: string;
  serial_number: string;
  technical_spec?: string | null;
  location?: string | null;
  max_rental_days: number;
  image_url?: string | null;
}

export async function getEquipment(filters: EquipmentFilters = {}): Promise<Equipment[]> {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, value]) => value !== undefined && value !== "")
  );
  const { data } = await api.get<Equipment[]>("/equipment", { params });
  return data;
}

export async function getEquipmentById(id: string): Promise<Equipment> {
  const { data } = await api.get<Equipment>(`/equipment/${id}`);
  return data;
}

export async function getEquipmentHistory(id: string): Promise<EquipmentHistoryItem[]> {
  const { data } = await api.get<EquipmentHistoryItem[]>(`/equipment/${id}/history`);
  return data;
}

export async function createEquipment(payload: EquipmentPayload): Promise<Equipment> {
  const { data } = await api.post<Equipment>("/equipment", payload);
  return data;
}

export async function updateEquipment(
  id: string,
  payload: Partial<EquipmentPayload & { status: EquipmentStatus }>
): Promise<Equipment> {
  const { data } = await api.put<Equipment>(`/equipment/${id}`, payload);
  return data;
}

export async function deleteEquipment(id: string): Promise<void> {
  await api.delete(`/equipment/${id}`);
}

export async function updateEquipmentStatus(
  id: string,
  status: EquipmentStatus
): Promise<Equipment> {
  const { data } = await api.patch<Equipment>(`/equipment/${id}/status`, { status });
  return data;
}
