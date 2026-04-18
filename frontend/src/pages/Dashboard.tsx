import { useEffect, useState } from "react";
import { api } from "../api";
import { useI18n } from "../i18n";

type Summary = {
  total: number;
  by_status: Record<string, number>;
  count: number;
};

export default function Dashboard() {
  const { t } = useI18n();
  const [status, setStatus] = useState<any>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [compliance, setCompliance] = useState<any[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const [s, c, cm] = await Promise.all([
          api.get("/status"),
          api.get<Summary>("/claims/summary"),
          api.get("/compliance"),
        ]);
        setStatus(s.data); setSummary(c.data); setCompliance(cm.data);
      } catch {}
    })();
  }, []);

  const compliantCount = compliance.filter((c) => c.status === "compliant").length;
  const complianceTotal = compliance.length || 1;

  return (
    <div>
      <h1 className="page-title">{t.dash.title}</h1>
      <p className="page-sub">{t.dash.sub}</p>
      <div className="grid grid-4">
        <div className="card">
          <h3>{t.dash.revenue}</h3>
          <div className="big">${(summary?.total || 0).toLocaleString()}</div>
        </div>
        <div className="card">
          <h3>{t.dash.episodes}</h3>
          <div className="big">{status?.episodes ?? 0}</div>
        </div>
        <div className="card">
          <h3>{t.dash.sessions}</h3>
          <div className="big">{status?.sessions ?? 0}</div>
        </div>
        <div className="card">
          <h3>{t.dash.compliance}</h3>
          <div className="big">{compliantCount}/{complianceTotal}</div>
        </div>
      </div>

      <div className="grid grid-3" style={{ marginTop: 24 }}>
        <div className="card" style={{ gridColumn: "span 2" }}>
          <h3>{t.dash.statusTitle}</h3>
          <table className="table">
            <tbody>
              {Object.entries(summary?.by_status || {}).map(([k, v]) => (
                <tr key={k}>
                  <td>{k}</td>
                  <td style={{ textAlign: "right" }}>${(v as number).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="card">
          <h3>{t.dash.pending}</h3>
          <div style={{ fontSize: 13, color: "var(--muted)", marginBottom: 6 }}>
            Draft: ${(summary?.by_status?.draft || 0).toLocaleString()}
          </div>
          <div style={{ fontSize: 13, color: "var(--muted)" }}>
            Stamped: ${(summary?.by_status?.stamped || 0).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
}
