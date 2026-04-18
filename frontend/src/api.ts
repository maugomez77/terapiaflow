import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const api = axios.create({ baseURL: BASE });

export type Patient = {
  id: string; name: string; phone: string; email: string; curp: string; rfc: string;
  insurance: string; insurance_policy: string; language: "es" | "en"; created_at: string;
};

export type Episode = {
  id: string; patient_id: string; therapist_id: string;
  diagnosis_cie10: string; diagnosis_text: string;
  authorized_sessions: number; used_sessions: number;
  authorization_code: string; start_date: string; end_date: string | null;
  status: "active" | "completed" | "cancelled" | "pending_auth";
  rate_mxn_per_session: number;
};

export type Session = {
  id: string; episode_id: string; date: string; duration_minutes: number;
  soap_subjective: string; soap_objective: string; soap_assessment: string; soap_plan: string;
  pain_before: number; pain_after: number; therapist_signature: string;
};

export type HomeExercise = {
  id: string; patient_id: string; name: string; sets: number; reps: string;
  frequency_per_week: number; cues: string; video_url: string | null;
  language: string; created_at: string;
};

export type Claim = {
  id: string; episode_id: string; patient_id: string; insurance: string;
  amount_mxn: number; iva_mxn: number; total_mxn: number;
  cfdi_uuid: string; cfdi_status: "draft" | "stamped" | "paid" | "rejected";
  issued_at: string; paid_at: string | null;
};

export type ComplianceCheck = {
  id: string; area: string; status: "compliant" | "action_needed" | "critical";
  findings: string[]; recommendations: string[]; checked_at: string;
};
