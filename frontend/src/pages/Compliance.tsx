import { useEffect, useState } from "react";
import { api, type ComplianceCheck } from "../api";
import { useI18n } from "../i18n";

export default function Compliance() {
  const { t, lang } = useI18n();
  const [checks, setChecks] = useState<ComplianceCheck[]>([]);
  const [loading, setLoading] = useState(false);

  const refresh = async () => {
    const r = await api.get<ComplianceCheck[]>("/compliance"); setChecks(r.data);
  };
  useEffect(() => { refresh(); }, []);

  const run = async () => {
    setLoading(true);
    try { await api.post(`/ai/compliance?language=${lang}`); refresh(); }
    finally { setLoading(false); }
  };

  const badgeClass = (s: string) =>
    s === "compliant" ? "badge-ok" :
    s === "action_needed" ? "badge-warn" : "badge-danger";

  // Only show latest check per area
  const byArea: Record<string, ComplianceCheck> = {};
  checks.forEach((c) => {
    if (!byArea[c.area] || byArea[c.area].checked_at < c.checked_at) byArea[c.area] = c;
  });

  return (
    <div>
      <h1 className="page-title">{t.compliance.title}</h1>
      <p className="page-sub">{t.compliance.sub}</p>
      <div style={{ marginBottom: 20 }}>
        <button className="btn" onClick={run} disabled={loading}>
          {loading ? t.common.loading : t.compliance.runCheck}
        </button>
      </div>
      <div className="grid grid-3">
        {Object.values(byArea).map((c) => (
          <div key={c.id} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <h3 style={{ color: "var(--text)", margin: 0 }}>{c.area}</h3>
              <span className={"badge " + badgeClass(c.status)}>{c.status}</span>
            </div>
            {c.findings.length > 0 && (
              <>
                <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>{t.compliance.findings}:</div>
                <ul style={{ fontSize: 12, marginTop: 0, paddingLeft: 18 }}>
                  {c.findings.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </>
            )}
            {c.recommendations.length > 0 && (
              <>
                <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>{t.compliance.recs}:</div>
                <ul style={{ fontSize: 12, marginTop: 0, paddingLeft: 18 }}>
                  {c.recommendations.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
