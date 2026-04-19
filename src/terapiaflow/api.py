"""TerapiaFlow FastAPI backend."""

from __future__ import annotations

from datetime import datetime, date
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import ai, demo, store, videos

app = FastAPI(title="TerapiaFlow API", version="0.1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)


class PatientIn(BaseModel):
    name: str; phone: str; email: str = ""
    curp: str = ""; rfc: str = ""
    insurance: str = "self_pay"; insurance_policy: str = ""
    language: Literal["es", "en"] = "es"


class EpisodeIn(BaseModel):
    patient_id: str
    diagnosis_cie10: str = ""
    diagnosis_text: str
    authorized_sessions: int
    authorization_code: str = ""
    rate_mxn_per_session: float = 600.0
    start_date: date


class SessionNoteRequest(BaseModel):
    episode_id: str
    subjective: str
    vitals: str = ""
    pain_before: int = 0
    pain_after: int = 0


class ExerciseRequest(BaseModel):
    patient_id: str
    diagnosis: str
    phase: str = "strength"
    language: Literal["es", "en"] = "es"


@app.get("/")
def root():
    return {
        "name": "TerapiaFlow API", "version": "0.1.0",
        "description": "PT compliance & progress platform for Morelia",
        "endpoints": ["/patients", "/episodes", "/sessions", "/home-exercises",
                       "/claims", "/compliance", "/ai/soap", "/ai/home-exercises",
                       "/ai/compliance", "/videos/resolve", "/status", "/demo/seed"],
    }


@app.get("/status")
def status():
    state = store.load()
    return {
        "patients": len(state["patients"]),
        "episodes": len(state["episodes"]),
        "sessions": len(state["sessions"]),
        "home_exercises": len(state["home_exercises"]),
        "claims": len(state["claims"]),
        "compliance_checks": len(state["compliance_checks"]),
        "revenue_mxn": sum(c["total_mxn"] for c in state["claims"]),
    }


@app.post("/demo/seed")
def seed(): demo.seed(); return {"ok": True}


@app.get("/patients")
def list_patients():
    return store.load()["patients"]


@app.post("/patients")
def create_patient(p: PatientIn):
    state = store.load()
    rec = {"id": store.new_id("pat"),
           "created_at": datetime.utcnow().isoformat(),
           **p.model_dump()}
    state["patients"].append(rec); store.save(state)
    return rec


@app.get("/episodes")
def list_episodes(patient_id: str | None = None):
    rows = store.load()["episodes"]
    return [e for e in rows if not patient_id or e["patient_id"] == patient_id]


@app.post("/episodes")
def create_episode(e: EpisodeIn):
    state = store.load()
    rec = {
        "id": store.new_id("epi"), "therapist_id": "thp_default",
        "used_sessions": 0, "end_date": None, "status": "active",
        **e.model_dump(),
    }
    rec["start_date"] = e.start_date.isoformat()
    state["episodes"].append(rec); store.save(state)
    return rec


@app.get("/sessions")
def list_sessions(episode_id: str | None = None):
    rows = store.load()["sessions"]
    return [s for s in rows if not episode_id or s["episode_id"] == episode_id]


@app.post("/ai/soap")
def ai_soap(req: SessionNoteRequest):
    state = store.load()
    epi = next((e for e in state["episodes"] if e["id"] == req.episode_id), None)
    if not epi: raise HTTPException(404, "episode not found")
    pat = next((p for p in state["patients"] if p["id"] == epi["patient_id"]), None)
    lang = pat["language"] if pat else "es"
    note = ai.generate_soap_note(epi["diagnosis_text"], req.subjective,
                                    req.vitals, language=lang)
    rec = {
        "id": store.new_id("ses"), "episode_id": req.episode_id,
        "date": datetime.utcnow().isoformat(),
        "duration_minutes": 50,
        "soap_subjective": note.get("soap_subjective", ""),
        "soap_objective": note.get("soap_objective", ""),
        "soap_assessment": note.get("soap_assessment", ""),
        "soap_plan": note.get("soap_plan", ""),
        "pain_before": req.pain_before, "pain_after": req.pain_after,
        "therapist_signature": "thp_default",
    }
    state["sessions"].append(rec)
    epi["used_sessions"] = epi.get("used_sessions", 0) + 1
    store.save(state)
    return rec


@app.get("/home-exercises")
def list_exercises(patient_id: str | None = None):
    rows = store.load()["home_exercises"]
    return [e for e in rows if not patient_id or e["patient_id"] == patient_id]


@app.post("/ai/home-exercises")
def ai_exercises(req: ExerciseRequest):
    state = store.load()
    exs = ai.generate_home_exercises(req.diagnosis, req.phase, language=req.language)
    rows = []
    for ex in exs:
        rec = {
            "id": store.new_id("hex"), "patient_id": req.patient_id,
            "video_url": None,
            "language": req.language,
            "created_at": datetime.utcnow().isoformat(),
            **ex,
        }
        state["home_exercises"].append(rec); rows.append(rec)
    store.save(state)
    return rows


@app.get("/claims")
def list_claims():
    return store.load()["claims"]


@app.get("/claims/summary")
def claims_summary():
    state = store.load()
    by: dict[str, float] = {"draft": 0, "stamped": 0, "paid": 0, "rejected": 0}
    for c in state["claims"]:
        by[c["cfdi_status"]] = by.get(c["cfdi_status"], 0) + c["total_mxn"]
    return {
        "total": sum(c["total_mxn"] for c in state["claims"]),
        "by_status": by,
        "count": len(state["claims"]),
    }


@app.post("/ai/compliance")
def ai_compliance(language: Literal["es", "en"] = "es"):
    state = store.load()
    snapshot = {
        "patients_count": len(state["patients"]),
        "episodes_active": sum(1 for e in state["episodes"] if e.get("status") == "active"),
        "sessions_with_soap": sum(1 for s in state["sessions"] if s.get("soap_objective")),
        "sessions_missing_soap": sum(1 for s in state["sessions"] if not s.get("soap_objective")),
        "claims_stamped": sum(1 for c in state["claims"] if c.get("cfdi_status") == "stamped"),
        "claims_draft": sum(1 for c in state["claims"] if c.get("cfdi_status") == "draft"),
    }
    checks = ai.run_compliance_check(snapshot, language=language)
    for c in checks:
        state["compliance_checks"].append({
            "id": store.new_id("cmp"),
            "area": c["area"], "status": c["status"],
            "findings": c.get("findings", []),
            "recommendations": c.get("recommendations", []),
            "checked_at": datetime.utcnow().isoformat(),
        })
    store.save(state)
    return checks


@app.get("/compliance")
def list_compliance():
    return store.load()["compliance_checks"]


@app.get("/videos/resolve")
def resolve_video(exercise: str, language: Literal["es", "en"] = "es"):
    return videos.resolve_video(exercise, language=language)
