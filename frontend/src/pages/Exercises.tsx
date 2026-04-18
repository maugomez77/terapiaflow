import { useEffect, useState } from "react";
import { api, type Patient, type HomeExercise } from "../api";
import { useI18n } from "../i18n";

export default function Exercises() {
  const { t, lang } = useI18n();
  const [pats, setPats] = useState<Patient[]>([]);
  const [list, setList] = useState<HomeExercise[]>([]);
  const [form, setForm] = useState({ patient_id: "", diagnosis: "", phase: "strength" });
  const [loading, setLoading] = useState(false);

  const refresh = async () => {
    const [p, e] = await Promise.all([
      api.get<Patient[]>("/patients"),
      api.get<HomeExercise[]>("/home-exercises"),
    ]);
    setPats(p.data); setList(e.data);
    if (!form.patient_id && p.data.length) setForm((f) => ({ ...f, patient_id: p.data[0].id }));
  };
  useEffect(() => { refresh(); }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try { await api.post("/ai/home-exercises", { ...form, language: lang }); refresh(); }
    finally { setLoading(false); }
  };

  const names = Object.fromEntries(pats.map((p) => [p.id, p.name]));

  return (
    <div>
      <h1 className="page-title">{t.exercises.title}</h1>
      <p className="page-sub">{t.exercises.sub}</p>
      <div className="card" style={{ marginBottom: 20 }}>
        <form className="form" style={{ gridTemplateColumns: "repeat(4, 1fr)", maxWidth: "none", display: "grid" }} onSubmit={submit}>
          <label>{t.patients.name}
            <select value={form.patient_id}
                    onChange={(e) => setForm({ ...form, patient_id: e.target.value })}>
              {pats.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </label>
          <label>{t.exercises.diagnosis}
            <input required value={form.diagnosis}
                    onChange={(e) => setForm({ ...form, diagnosis: e.target.value })} />
          </label>
          <label>{t.exercises.phase}
            <select value={form.phase} onChange={(e) => setForm({ ...form, phase: e.target.value })}>
              <option value="acute">acute</option>
              <option value="strength">strength</option>
              <option value="return_to_sport">return to sport</option>
            </select>
          </label>
          <button className="btn" disabled={loading} style={{ alignSelf: "end" }}>
            {loading ? t.common.loading : t.exercises.prescribe}
          </button>
        </form>
      </div>

      <div className="card">
        <table className="table">
          <thead><tr>
            <th>{t.patients.name}</th><th>Ejercicio</th>
            <th>Sets × Reps</th><th>Frec/sem</th><th>{t.exercises.cues}</th>
          </tr></thead>
          <tbody>
            {list.map((e) => (
              <tr key={e.id}>
                <td>{names[e.patient_id] || e.patient_id}</td>
                <td>{e.name}</td>
                <td>{e.sets} × {e.reps}</td>
                <td>{e.frequency_per_week}</td>
                <td style={{ fontSize: 12, color: "var(--muted)" }}>{e.cues}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
