import api from "./client";
import { TokenResponse, User } from "../types";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload extends LoginPayload {
  full_name: string;
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/login", payload);
  return data;
}

export async function register(payload: RegisterPayload): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/register", payload);
  return data;
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>("/auth/me");
  return data;
}

export async function getKeycloakLoginUrl(): Promise<string> {
  const { data } = await api.get<{ url: string }>("/auth/keycloak/login");
  return data.url;
}

export async function getKeycloakRegisterUrl(): Promise<string> {
  const { data } = await api.get<{ url: string }>("/auth/keycloak/register");
  return data.url;
}

export async function getKeycloakLogoutUrl(): Promise<string> {
  const { data } = await api.get<{ url: string }>("/auth/keycloak/logout");
  return data.url;
}

export async function completeKeycloakLogin(code: string): Promise<TokenResponse> {
  const { data } = await api.get<TokenResponse>("/auth/keycloak/callback", {
    params: { code }
  });
  return data;
}
