import type { Notification } from "../types";

import api from "./client";

export async function getNotifications() {
  const { data } = await api.get<Notification[]>("/notifications");
  return data;
}
