import api from "./client";
import { FaultReport } from "../types";

export interface FaultReportPayload {
  equipment_id: string;
  description: string;
}

export async function createFaultReport(payload: FaultReportPayload): Promise<FaultReport> {
  const { data } = await api.post<FaultReport>("/fault-reports", payload);
  return data;
}

export async function getFaultReports(equipmentId?: string): Promise<FaultReport[]> {
  const { data } = await api.get<FaultReport[]>("/fault-reports", {
    params: equipmentId ? { equipment_id: equipmentId } : undefined
  });
  return data;
}

export async function resolveFaultReport(id: string): Promise<FaultReport> {
  const { data } = await api.patch<FaultReport>(`/fault-reports/${id}/resolve`);
  return data;
}
