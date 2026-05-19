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
