export type UserRole = "student" | "staff" | "equipment_manager" | "admin";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active?: boolean;
  created_at?: string;
}

export type EquipmentStatus =
  | "available"
  | "reserved"
  | "borrowed"
  | "damaged";

export interface Equipment {
  id: string;
  name: string;
  type: string;
  serial_number: string;
  technical_spec?: string | null;
  location?: string | null;
  status: EquipmentStatus;
  max_rental_days: number;
  image_url?: string | null;
  created_at: string;
  updated_at: string;
}

export type ReservationStatus = "pending" | "active" | "completed" | "cancelled";

export interface Reservation {
  id: string;
  user_id: string;
  equipment_id: string;
  start_date: string;
  end_date: string;
  status: ReservationStatus;
  created_at: string;
  user: User;
  equipment: Equipment;
}

export interface EquipmentHistoryItem {
  id: string;
  start_date: string;
  end_date: string;
  status: string;
  user: {
    full_name: string;
    email: string;
    role: string;
  };
  return_info?: {
    returned_at: string;
    condition: string;
    notes?: string | null;
  } | null;
}

export interface ReturnRecord {
  id: string;
  reservation_id: string;
  returned_at: string;
  condition: "good" | "damaged";
  notes?: string | null;
  reported_by: string;
}

export interface FaultReport {
  id: string;
  equipment_id: string;
  user_id: string;
  description: string;
  created_at: string;
  resolved_at?: string | null;
}

export interface Notification {
  id: string;
  type: "email" | "sms" | string;
  message: string;
  sent_at: string;
  reservation_id: string;
}

export interface RentalStatistics {
  total_equipment: number;
  total_reservations: number;
  active_reservations: number;
  completed_reservations: number;
  cancelled_reservations: number;
  equipment_by_status: Record<EquipmentStatus, number>;
  most_rented_equipment: Array<{
    name: string;
    type: string;
    rental_count: number;
  }>;
  fault_reports_unresolved: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
  user: User;
}

export interface ApiErrorDetail {
  detail?: string;
  reasons?: string[];
  score?: number;
}
