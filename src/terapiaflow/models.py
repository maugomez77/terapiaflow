"""TerapiaFlow models — focused on practice mgmt + compliance."""

from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel, Field


InsuranceType = Literal["imss", "issste", "gnp", "axa", "metlife", "private", "self_pay", "other"]


class Patient(BaseModel):
    id: str
    name: str
    curp: str = ""
    phone: str
    email: str = ""
    rfc: str = ""
    insurance: InsuranceType = "self_pay"
    insurance_policy: str = ""
    language: Literal["es", "en"] = "es"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Episode(BaseModel):
    """Billable treatment episode tied to an authorization."""
    id: str
    patient_id: str
    therapist_id: str
    diagnosis_cie10: str = ""
    diagnosis_text: str
    authorized_sessions: int
    used_sessions: int = 0
    authorization_code: str = ""
    start_date: date
    end_date: date | None = None
    status: Literal["active", "completed", "cancelled", "pending_auth"] = "active"
    rate_mxn_per_session: float = 600.0


class Session(BaseModel):
    id: str
    episode_id: str
    date: datetime
    duration_minutes: int = 50
    soap_subjective: str = ""
    soap_objective: str = ""
    soap_assessment: str = ""
    soap_plan: str = ""
    pain_before: int = 0
    pain_after: int = 0
    therapist_signature: str = ""


class HomeExercise(BaseModel):
    id: str
    patient_id: str
    name: str
    sets: int
    reps: str
    frequency_per_week: int
    cues: str = ""
    video_url: str | None = None
    language: Literal["es", "en"] = "es"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Claim(BaseModel):
    """CFDI 4.0 invoice record."""
    id: str
    episode_id: str
    patient_id: str
    insurance: InsuranceType
    amount_mxn: float
    iva_mxn: float
    total_mxn: float
    cfdi_uuid: str = ""
    cfdi_status: Literal["draft", "stamped", "paid", "rejected"] = "draft"
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: datetime | None = None


class ComplianceCheck(BaseModel):
    id: str
    area: Literal["nom_004", "cofepris", "privacy_lfpdppp", "cfdi", "imss_billing"]
    status: Literal["compliant", "action_needed", "critical"]
    findings: list[str]
    recommendations: list[str]
    checked_at: datetime = Field(default_factory=datetime.utcnow)
