# TerapiaFlow

**PT compliance & practice management for physical therapy clinics in Morelia, Michoacán.**

Built from Council deep session 2026-04-18 (`council-2026-04-18-b5c7`) — #3 pick (judge confidence 6.8, 22/36 votes).

## What it does
- Tracks treatment episodes, authorizations, and session allotments per insurer
- Generates NOM-004-SSA3 compliant SOAP notes from trainer subjective input
- Prescribes AI-generated home exercises with clear patient cues
- Tracks CFDI 4.0 billing status (IMSS, GNP, AXA, MetLife, self-pay, etc.)
- Runs compliance audits across NOM-004, COFEPRIS, LFPDPPP, CFDI, IMSS billing
- Bilingual ES/EN per patient

## Stack
- CLI: typer + rich · API: FastAPI · Frontend: React + TypeScript + Vite
- AI: Claude Haiku 4.5 · Storage: JSON (`~/.terapiaflow/store.json`)
- Deploy: Vercel (frontend) + Render (backend)

## Quick start
```bash
pip install -e .
export ANTHROPIC_API_KEY=sk-ant-...
terapiaflow demo
terapiaflow patients list
terapiaflow episodes list
terapiaflow compliance check
terapiaflow serve
```

Frontend:
```bash
cd frontend && npm install && npm run dev
```

## CLI
```
terapiaflow patients list
terapiaflow episodes list
terapiaflow sessions note <episode_id> "<subjective>"
terapiaflow exercises prescribe <patient_id> "<diagnosis>" --phase strength
terapiaflow claims list|summary
terapiaflow compliance check
terapiaflow demo|status|serve
```
