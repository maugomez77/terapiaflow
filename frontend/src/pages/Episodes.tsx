import { useEffect, useState } from "react";
import { api, type Episode, type Patient } from "../api";
import { useI18n } from "../i18n";

export default function Episodes() {
  const { t } = useI18n();
  const [eps, setEps] = useState<Episode[]>([]);
  const [pats, setPats] = useState<Patient[]>([]);

  useEffect(() => {
    (async () => {
      const [e, p] = await Promise.all([
        api.get<Episode[]>("/episodes"), api.get<Patient[]>("/patients"),
      ]);
      setEps(e.data); setPats(p.data);
    })();
  }, []);

  const names = Object.fromEntries(pats.map((p) => [p.id, p.name]));

  return (
    <div>
      <h1 className="page-title">{t.episodes.title}</h1>
      <p className="page-sub">{t.episodes.sub}</p>
      <div className="card">
        <table className="table">
          <thead><tr>
            <th>{t.patients.name}</th>
            <th>{t.episodes.diagnosis}</th>
            <th>{t.episodes.auth}</th>
            <th>{t.episodes.used}</th>
            <th>{t.episodes.rate}</th>
            <th>{t.episodes.status}</th>
          </tr></thead>
          <tbody>
            {eps.map((e) => {
              const pct = (e.used_sessions / (e.authorized_sessions || 1)) * 100;
              return (
                <tr key={e.id}>
                  <td>{names[e.patient_id] || e.patient_id}</td>
                  <td>{e.diagnosis_text}</td>
                  <td style={{ fontSize: 11 }}>{e.authorization_code || "—"}</td>
                  <td>
                    {e.used_sessions}/{e.authorized_sessions}
                    <div className="bar"><span style={{ width: `${Math.min(pct, 100)}%` }} /></div>
                  </td>
                  <td>${e.rate_mxn_per_session.toFixed(0)}</td>
                  <td><span className={"badge " +
                    (e.status === "active" ? "badge-ok" :
                     e.status === "pending_auth" ? "badge-warn" : "")}>{e.status}</span></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
