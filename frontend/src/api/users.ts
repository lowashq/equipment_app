import api from "./client";
import { User, UserRole } from "../types";

export async function getUsers(): Promise<User[]> {
  const { data } = await api.get<User[]>("/users");
  return data;
}

export async function updateUserRole(userId: string, role: UserRole): Promise<User> {
  const { data } = await api.patch<User>(`/users/${userId}/role`, { role });
  return data;
}
