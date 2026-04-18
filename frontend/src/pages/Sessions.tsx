import { useEffect, useState } from "react";
import { api, type Episode, type Patient, type Session } from "../api";
import { useI18n } from "../i18n";

export default function Sessions() {
  const { t } = useI18n();
  const [eps, setEps] = useState<Episode[]>([]);
  const [pats, setPats] = useState<Patient[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [episodeId, setEpisodeId] = useState("");
  const [form, setForm] = useState({ subjective: "", vitals: "", pain_before: 5, pain_after: 3 });
  const [loading, setLoading] = useState(false);

  const refresh = async () => {
    const [e, p, s] = await Promise.all([
      api.get<Episode[]>("/episodes"),
      api.get<Patient[]>("/patients"),
      api.get<Session[]>("/sessions"),
    ]);
    setEps(e.data); setPats(p.data); setSessions(s.data);
    if (!episodeId && e.data.length) setEpisodeId(e.data[0].id);
  };
  useEffect(() => { refresh(); }, []);

  const submit = async (ev: React.FormEvent) => {
    ev.preventDefault();
    setLoading(true);
    try {
      await api.post("/ai/soap", { episode_id: episodeId, ...form });
      setForm({ subjective: "", vitals: "", pain_before: 5, pain_after: 3 });
      refresh();
    } finally { setLoading(false); }
  };

  const names = Object.fromEntries(pats.map((p) => [p.id, p.name]));
  const epLabel = (ep: Episode) => `${names[ep.patient_id] || "?"} — ${ep.diagnosis_text}`;

  return (
    <div>
      <h1 className="page-title">{t.sessions.title}</h1>
      <p className="page-sub">{t.sessions.sub}</p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        <div className="card">
          <form className="form" onSubmit={submit}>
            <label>{t.episodes.title}
              <select value={episodeId} onChange={(e) => setEpisodeId(e.target.value)}>
                {eps.map((e) => <option key={e.id} value={e.id}>{epLabel(e)}</option>)}
              </select>
            </label>
            <label>{t.sessions.subjective}
              <textarea required rows={3} value={form.subjective}
                        onChange={(e) => setForm({ ...form, subjective: e.target.value })} />
            </label>
            <label>{t.sessions.vitals}
              <textarea rows={2} value={form.vitals}
                        onChange={(e) => setForm({ ...form, vitals: e.target.value })} />
            </label>
            <label>{t.sessions.painBefore}
              <input type="number" min={0} max={10} value={form.pain_before}
                     onChange={(e) => setForm({ ...form, pain_before: +e.target.value })} />
            </label>
            <label>{t.sessions.painAfter}
              <input type="number" min={0} max={10} value={form.pain_after}
                     onChange={(e) => setForm({ ...form, pain_after: +e.target.value })} />
            </label>
            <button className="btn" disabled={loading}>
              {loading ? t.common.loading : t.sessions.generate}
            </button>
          </form>
        </div>
        <div style={{ maxHeight: "80vh", overflow: "auto" }}>
          {sessions.slice().reverse().slice(0, 8).map((s) => (
            <div key={s.id} className="card" style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 6 }}>
                {new Date(s.date).toLocaleString()} · dolor {s.pain_before}→{s.pain_after}
              </div>
              <div className="soap">
                <div><span className="soap-label">S.</span> {s.soap_subjective}</div>
                <div><span className="soap-label">O.</span> {s.soap_objective}</div>
                <div><span className="soap-label">A.</span> {s.soap_assessment}</div>
                <div><span className="soap-label">P.</span> {s.soap_plan}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
