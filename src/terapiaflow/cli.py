"""TerapiaFlow CLI."""

from __future__ import annotations

from datetime import datetime, date

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import ai, demo, store

app = typer.Typer(help="PT compliance & progress platform for Morelia clinics.")
console = Console()

patients_app = typer.Typer()
episodes_app = typer.Typer()
sessions_app = typer.Typer()
exercises_app = typer.Typer()
claims_app = typer.Typer()
compliance_app = typer.Typer()

app.add_typer(patients_app, name="patients")
app.add_typer(episodes_app, name="episodes")
app.add_typer(sessions_app, name="sessions")
app.add_typer(exercises_app, name="exercises")
app.add_typer(claims_app, name="claims")
app.add_typer(compliance_app, name="compliance")


@patients_app.command("list")
def patients_list() -> None:
    state = store.load()
    t = Table(title="Pacientes")
    for c in ("ID", "Nombre", "Teléfono", "Seguro", "Idioma"):
        t.add_column(c)
    for p in state["patients"]:
        t.add_row(p["id"], p["name"], p["phone"], p["insurance"], p["language"])
    console.print(t)


@episodes_app.command("list")
def episodes_list() -> None:
    state = store.load()
    names = {p["id"]: p["name"] for p in state["patients"]}
    t = Table(title="Episodios de tratamiento")
    for c in ("ID", "Paciente", "Diagnóstico", "Sesiones", "Estado", "Tarifa"):
        t.add_column(c)
    for e in state["episodes"]:
        t.add_row(e["id"], names.get(e["patient_id"], "?"),
                   e["diagnosis_text"][:30],
                   f"{e['used_sessions']}/{e['authorized_sessions']}",
                   e["status"], f"${e['rate_mxn_per_session']:.0f}")
    console.print(t)


@sessions_app.command("note")
def sessions_note(episode_id: str, subjective: str, vitals: str = "",
                   pain_before: int = 0, pain_after: int = 0) -> None:
    state = store.load()
    epi = next((e for e in state["episodes"] if e["id"] == episode_id), None)
    if not epi:
        console.print("[red]Episode not found[/red]"); raise typer.Exit(1)
    pat = next((p for p in state["patients"] if p["id"] == epi["patient_id"]), None)
    note = ai.generate_soap_note(epi["diagnosis_text"], subjective, vitals,
                                    language=pat["language"] if pat else "es")  # type: ignore[arg-type]
    rec = {
        "id": store.new_id("ses"),
        "episode_id": episode_id,
        "date": datetime.utcnow().isoformat(),
        "duration_minutes": 50,
        "soap_subjective": note.get("soap_subjective", ""),
        "soap_objective": note.get("soap_objective", ""),
        "soap_assessment": note.get("soap_assessment", ""),
        "soap_plan": note.get("soap_plan", ""),
        "pain_before": pain_before,
        "pain_after": pain_after,
        "therapist_signature": "thp_default",
    }
    state["sessions"].append(rec)
    epi["used_sessions"] = epi.get("used_sessions", 0) + 1
    store.save(state)
    console.print(Panel.fit(
        f"[bold]S:[/bold] {rec['soap_subjective']}\n"
        f"[bold]O:[/bold] {rec['soap_objective']}\n"
        f"[bold]A:[/bold] {rec['soap_assessment']}\n"
        f"[bold]P:[/bold] {rec['soap_plan']}",
        title=f"SOAP — episodio {episode_id}"))


@exercises_app.command("prescribe")
def exercises_prescribe(patient_id: str, diagnosis: str, phase: str = "strength",
                         language: str = "es") -> None:
    state = store.load()
    exs = ai.generate_home_exercises(diagnosis, phase, language=language)  # type: ignore[arg-type]
    rows = []
    for ex in exs:
        rec = {
            "id": store.new_id("hex"),
            "patient_id": patient_id,
            "name": ex.get("name", ""),
            "sets": ex.get("sets", 3),
            "reps": ex.get("reps", "10"),
            "frequency_per_week": ex.get("frequency_per_week", 5),
            "cues": ex.get("cues", ""),
            "video_url": None,
            "language": language,
            "created_at": datetime.utcnow().isoformat(),
        }
        state["home_exercises"].append(rec)
        rows.append(rec)
    store.save(state)
    t = Table(title="Ejercicios prescritos")
    for c in ("Nombre", "Sets", "Reps", "Frec/sem", "Pistas"):
        t.add_column(c)
    for r in rows:
        t.add_row(r["name"], str(r["sets"]), r["reps"],
                   str(r["frequency_per_week"]), r["cues"][:40])
    console.print(t)


@claims_app.command("list")
def claims_list() -> None:
    state = store.load()
    names = {p["id"]: p["name"] for p in state["patients"]}
    t = Table(title="Facturación CFDI")
    for c in ("ID", "Paciente", "Seguro", "Total MXN", "Estado CFDI"):
        t.add_column(c)
    for cl in state["claims"]:
        t.add_row(cl["id"], names.get(cl["patient_id"], "?"),
                   cl["insurance"], f"${cl['total_mxn']:.2f}",
                   cl["cfdi_status"])
    console.print(t)


@claims_app.command("summary")
def claims_summary() -> None:
    state = store.load()
    by = {"draft": 0, "stamped": 0, "paid": 0, "rejected": 0}
    total = 0.0
    for c in state["claims"]:
        by[c["cfdi_status"]] = by.get(c["cfdi_status"], 0) + c["total_mxn"]
        total += c["total_mxn"]
    console.print(Panel.fit(
        f"Total facturado: ${total:,.2f} MXN\n"
        f"Pagado: ${by.get('paid', 0):,.2f}\n"
        f"Timbrado (pendiente pago): ${by.get('stamped', 0):,.2f}\n"
        f"Borrador: ${by.get('draft', 0):,.2f}\n"
        f"Rechazado: ${by.get('rejected', 0):,.2f}",
        title="Resumen de facturación"))


@compliance_app.command("check")
def compliance_check(language: str = "es") -> None:
    state = store.load()
    snapshot = {
        "patients_count": len(state["patients"]),
        "episodes_active": sum(1 for e in state["episodes"] if e.get("status") == "active"),
        "sessions_with_soap":
            sum(1 for s in state["sessions"] if s.get("soap_objective")),
        "sessions_missing_soap":
            sum(1 for s in state["sessions"] if not s.get("soap_objective")),
        "claims_stamped": sum(1 for c in state["claims"] if c.get("cfdi_status") == "stamped"),
        "claims_draft": sum(1 for c in state["claims"] if c.get("cfdi_status") == "draft"),
    }
    checks = ai.run_compliance_check(snapshot, language=language)  # type: ignore[arg-type]
    for c in checks:
        state["compliance_checks"].append({
            "id": store.new_id("cmp"),
            "area": c["area"], "status": c["status"],
            "findings": c.get("findings", []),
            "recommendations": c.get("recommendations", []),
            "checked_at": datetime.utcnow().isoformat(),
        })
    store.save(state)
    t = Table(title="Auditoría de cumplimiento")
    for col in ("Área", "Estado", "Hallazgos", "Recomendaciones"):
        t.add_column(col)
    for c in checks:
        t.add_row(c["area"], c["status"],
                   "; ".join(c.get("findings", []))[:60],
                   "; ".join(c.get("recommendations", []))[:60])
    console.print(t)


@app.command("demo")
def demo_cmd() -> None:
    demo.seed()
    console.print("[green]✓[/green] Demo data seeded")


@app.command("status")
def status() -> None:
    state = store.load()
    rev = sum(c["total_mxn"] for c in state["claims"])
    console.print(Panel.fit(
        f"Patients: {len(state['patients'])}\n"
        f"Episodes: {len(state['episodes'])}\n"
        f"Sessions: {len(state['sessions'])}\n"
        f"Home exercise prescriptions: {len(state['home_exercises'])}\n"
        f"Claims: {len(state['claims'])} (${rev:,.2f} MXN)\n"
        f"Compliance checks: {len(state['compliance_checks'])}",
        title="TerapiaFlow status"))


@app.command("serve")
def serve(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn
    uvicorn.run("terapiaflow.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    app()
