import api from "./client";
import { ReturnRecord } from "../types";

export interface ReturnPayload {
  reservation_id: string;
  condition: "good" | "damaged";
  notes?: string | null;
}

export async function registerReturn(payload: ReturnPayload): Promise<ReturnRecord> {
  const { data } = await api.post<ReturnRecord>("/returns", payload);
  return data;
}
