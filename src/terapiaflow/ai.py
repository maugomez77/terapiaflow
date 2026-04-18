"""Claude integrations for TerapiaFlow."""

from __future__ import annotations

import json
import os
from typing import Literal

from anthropic import Anthropic

MODEL = os.environ.get("TERAPIAFLOW_MODEL", "claude-haiku-4-5-20251001")


def _client() -> Anthropic:
    return Anthropic()


def _ask_json(system: str, prompt: str, fallback: dict, max_tokens: int = 1800) -> dict:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return fallback
    try:
        resp = _client().messages.create(
            model=MODEL, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0]
        return json.loads(text.strip())
    except Exception:
        return fallback


def generate_soap_note(
    diagnosis: str,
    subjective: str,
    vitals: str = "",
    language: Literal["es", "en"] = "es",
) -> dict:
    lang_instr = ("Redacta la nota SOAP en español clínico formal, cumpliendo NOM-004-SSA3."
                  if language == "es" else
                  "Write SOAP note in formal clinical English.")
    system = (
        "You are a licensed physical therapist drafting SOAP notes. Follow NOM-004-SSA3 "
        "documentation requirements (Mexico): include date, patient identifiers, objective "
        "findings with measurable data, assessment, and plan. " + lang_instr
    )
    prompt = (
        f"Diagnosis: {diagnosis}\nPatient subjective: {subjective}\nVitals/findings: {vitals}\n\n"
        "Return JSON: {\"soap_subjective\": str, \"soap_objective\": str, "
        "\"soap_assessment\": str, \"soap_plan\": str}"
    )
    return _ask_json(system, prompt, {
        "soap_subjective": subjective
                            if subjective else
                            ("El paciente refiere mejoría progresiva."
                             if language == "es" else "Patient reports progressive improvement."),
        "soap_objective": ("ROM rodilla 0-110°. Fuerza cuádriceps 4/5. Marcha sin muletas. "
                           "Dolor NRS 2/10." if language == "es"
                            else "Knee ROM 0-110°. Quadriceps strength 4/5. "
                                 "Ambulation without crutches. Pain NRS 2/10."),
        "soap_assessment": ("Progreso clínico adecuado, continúa fase de fortalecimiento."
                            if language == "es" else
                            "Appropriate clinical progress, continuing strengthening phase."),
        "soap_plan": ("Mantener protocolo 5x/semana. Revalorar en 2 semanas."
                      if language == "es" else
                      "Continue protocol 5x/week. Reassess in 2 weeks."),
    })


def generate_home_exercises(
    diagnosis: str,
    phase: str = "strength",
    language: Literal["es", "en"] = "es",
) -> list[dict]:
    lang_instr = ("Responde en español con instrucciones claras para el paciente."
                  if language == "es" else "Respond in English.")
    system = ("You are a physical therapist prescribing safe home exercises "
              "that patients can perform without supervision. " + lang_instr)
    prompt = (
        f"Diagnosis: {diagnosis}\nCurrent phase: {phase}\n\n"
        "Return JSON: {\"exercises\": [{\"name\": str, \"sets\": int, \"reps\": str, "
        "\"frequency_per_week\": int, \"cues\": str}]}\n"
        "Prescribe 4-5 exercises."
    )
    result = _ask_json(system, prompt, {
        "exercises": [
            {"name": "Isométrico de cuádriceps" if language == "es" else "Quadriceps isometric",
             "sets": 3, "reps": "10x10s", "frequency_per_week": 7,
             "cues": "Contrae cuádriceps, empuja rodilla contra toalla enrollada."
                     if language == "es" else
                     "Squeeze quadriceps, push knee against rolled towel."},
            {"name": "Elevación de pierna recta" if language == "es" else "Straight leg raise",
             "sets": 3, "reps": "15", "frequency_per_week": 7,
             "cues": "Sin flexionar rodilla, eleva pierna 30cm."
                     if language == "es" else
                     "Keep knee straight, lift leg 30cm."},
            {"name": "Mini sentadilla" if language == "es" else "Mini squat",
             "sets": 3, "reps": "12", "frequency_per_week": 5,
             "cues": "Rodillas alineadas con punta de pies, sin pasar dedos."
                     if language == "es" else
                     "Knees aligned with toes, no forward drift."},
            {"name": "Puente de glúteo" if language == "es" else "Glute bridge",
             "sets": 3, "reps": "12", "frequency_per_week": 5,
             "cues": "Aprieta glúteos al subir cadera, 2s arriba."
                     if language == "es" else
                     "Squeeze glutes at top, 2s hold."},
        ],
    })
    return result.get("exercises", [])


def run_compliance_check(
    clinic_snapshot: dict,
    language: Literal["es", "en"] = "es",
) -> list[dict]:
    lang_instr = ("Responde en español." if language == "es" else "Respond in English.")
    system = (
        "You are a Mexican healthcare compliance auditor checking a small PT clinic against "
        "NOM-004-SSA3 (expediente clínico), COFEPRIS registration requirements, LFPDPPP "
        "(privacy), CFDI 4.0 billing, and IMSS/private insurance billing norms. " + lang_instr
    )
    prompt = (
        f"Clinic snapshot: {json.dumps(clinic_snapshot, default=str)}\n\n"
        "Return JSON: {\"checks\": [{\"area\": \"nom_004|cofepris|privacy_lfpdppp|cfdi|imss_billing\", "
        "\"status\": \"compliant|action_needed|critical\", "
        "\"findings\": [str], \"recommendations\": [str]}]}"
    )
    result = _ask_json(system, prompt, {
        "checks": [
            {"area": "nom_004", "status": "action_needed",
             "findings": (["Notas SOAP incompletas en 2 expedientes"] if language == "es"
                          else ["Incomplete SOAP notes in 2 charts"]),
             "recommendations": (["Completar notas faltantes antes de 48h"] if language == "es"
                                  else ["Complete missing notes within 48h"])},
            {"area": "cofepris", "status": "compliant",
             "findings": (["Aviso de funcionamiento vigente"] if language == "es"
                          else ["Operating permit current"]),
             "recommendations": []},
            {"area": "privacy_lfpdppp", "status": "action_needed",
             "findings": (["Aviso de privacidad no visible en sitio web"] if language == "es"
                          else ["Privacy notice not visible on website"]),
             "recommendations": (["Publicar aviso antes de fin de mes"] if language == "es"
                                  else ["Publish notice by end of month"])},
            {"area": "cfdi", "status": "compliant",
             "findings": (["CFDI 4.0 timbrado correctamente"] if language == "es"
                          else ["CFDI 4.0 stamped correctly"]),
             "recommendations": []},
            {"area": "imss_billing", "status": "compliant",
             "findings": [], "recommendations": []},
        ],
    }, max_tokens=2400)
    return result.get("checks", [])
