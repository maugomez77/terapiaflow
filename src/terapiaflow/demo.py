"""TerapiaFlow demo seed — Morelia PT clinic."""

from datetime import datetime, timedelta, date

from . import store

THERAPIST = "thp_default"

PATIENTS = [
    {"name": "Sofía Ramírez", "curp": "RAMX000001HMCABC01", "phone": "+524431010101",
     "email": "sofia@example.mx", "rfc": "RASO000101AB1", "insurance": "gnp",
     "insurance_policy": "GNP-12345", "language": "es"},
    {"name": "Pedro González", "curp": "GOPX000002HMCABC02", "phone": "+524432020202",
     "email": "pedro@example.mx", "rfc": "", "insurance": "imss",
     "insurance_policy": "IMSS-98765", "language": "es"},
    {"name": "Julia Campos", "curp": "CAJX000003MMCABC03", "phone": "+524433030303",
     "email": "julia@example.mx", "rfc": "CAJU000101CD2", "insurance": "axa",
     "insurance_policy": "AXA-55555", "language": "es"},
    {"name": "Andrew Miller", "curp": "", "phone": "+524434040404",
     "email": "andrew@example.com", "rfc": "", "insurance": "self_pay",
     "insurance_policy": "", "language": "en"},
    {"name": "Laura Vega", "curp": "VELX000005MMCABC05", "phone": "+524435050505",
     "email": "laura@example.mx", "rfc": "VELA000101EF3", "insurance": "metlife",
     "insurance_policy": "ML-77788", "language": "es"},
]

EPISODES = [
    {"diagnosis_cie10": "M23.5", "diagnosis_text": "Inestabilidad crónica de rodilla post-LCA",
     "authorized_sessions": 24, "used_sessions": 9, "authorization_code": "GNP-AUT-2026-0128",
     "status": "active", "rate_mxn_per_session": 800.0},
    {"diagnosis_cie10": "M75.1", "diagnosis_text": "Síndrome manguito rotador",
     "authorized_sessions": 15, "used_sessions": 5, "authorization_code": "IMSS-2026-04-556",
     "status": "active", "rate_mxn_per_session": 450.0},
    {"diagnosis_cie10": "M54.5", "diagnosis_text": "Lumbalgia mecánica",
     "authorized_sessions": 10, "used_sessions": 8, "authorization_code": "AXA-PT-2026-778",
     "status": "active", "rate_mxn_per_session": 750.0},
    {"diagnosis_cie10": "S93.4", "diagnosis_text": "Ankle sprain grade II, left",
     "authorized_sessions": 8, "used_sessions": 4, "authorization_code": "",
     "status": "active", "rate_mxn_per_session": 900.0},
]


def seed() -> dict:
    state = store.load()
    if state.get("patients"):
        return state

    for p in PATIENTS:
        pid = store.new_id("pat")
        state["patients"].append({
            "id": pid,
            "created_at": datetime.utcnow().isoformat(),
            **p,
        })

    for i, e in enumerate(EPISODES):
        if i >= len(state["patients"]): break
        pid = state["patients"][i]["id"]
        eid = store.new_id("epi")
        start = date.today() - timedelta(days=30 - i * 5)
        state["episodes"].append({
            "id": eid, "patient_id": pid, "therapist_id": THERAPIST,
            "start_date": start.isoformat(),
            "end_date": None,
            **e,
        })
        # sessions
        for s in range(e["used_sessions"]):
            state["sessions"].append({
                "id": store.new_id("ses"),
                "episode_id": eid,
                "date": (datetime.utcnow() - timedelta(days=(e["used_sessions"] - s) * 3)).isoformat(),
                "duration_minutes": 50,
                "soap_subjective": "Paciente refiere mejoría" if i < 3 else "Patient reports improvement",
                "soap_objective": "ROM mejorado, fuerza 4/5",
                "soap_assessment": "Progreso clínico adecuado",
                "soap_plan": "Continuar protocolo",
                "pain_before": max(2, 6 - s),
                "pain_after": max(1, 4 - s),
                "therapist_signature": THERAPIST,
            })
        # claims
        amount = e["used_sessions"] * e["rate_mxn_per_session"]
        iva = round(amount * 0.16, 2)
        state["claims"].append({
            "id": store.new_id("clm"),
            "episode_id": eid,
            "patient_id": pid,
            "insurance": state["patients"][i]["insurance"],
            "amount_mxn": amount,
            "iva_mxn": iva,
            "total_mxn": round(amount + iva, 2),
            "cfdi_uuid": "" if i % 2 else f"A1B2-{i}-FAKE-UUID",
            "cfdi_status": "paid" if i == 0 else "stamped" if i < 3 else "draft",
            "issued_at": datetime.utcnow().isoformat(),
            "paid_at": datetime.utcnow().isoformat() if i == 0 else None,
        })
        # home exercises
        state["home_exercises"].extend([
            {"id": store.new_id("hex"), "patient_id": pid,
             "name": "Isométrico cuádriceps",
             "sets": 3, "reps": "10x10s", "frequency_per_week": 7,
             "cues": "Contrae 10s, descansa 5s.",
             "video_url": None, "language": state["patients"][i]["language"],
             "created_at": datetime.utcnow().isoformat()},
            {"id": store.new_id("hex"), "patient_id": pid,
             "name": "Puente de glúteo",
             "sets": 3, "reps": "12", "frequency_per_week": 5,
             "cues": "Aprieta glúteos, 2s arriba.",
             "video_url": None, "language": state["patients"][i]["language"],
             "created_at": datetime.utcnow().isoformat()},
        ])

    store.save(state)
    return state
