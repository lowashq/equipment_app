import api from "./client";
import { RentalStatistics } from "../types";

export async function getRentalStatistics(): Promise<RentalStatistics> {
  const { data } = await api.get<RentalStatistics>("/reports/statistics");
  return data;
}

export async function downloadReport(type: "csv" | "pdf"): Promise<void> {
  const response = await api.get<Blob>(`/reports/export/${type}`, {
    responseType: "blob"
  });
  const blob = new Blob([response.data], {
    type: type === "csv" ? "text/csv" : "application/pdf"
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = type === "csv" ? "rentals.csv" : "rentals.pdf";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
