import { useEffect, useState } from "react";
import { api, type Claim, type Patient } from "../api";
import { useI18n } from "../i18n";

export default function Billing() {
  const { t } = useI18n();
  const [claims, setClaims] = useState<Claim[]>([]);
  const [pats, setPats] = useState<Patient[]>([]);

  useEffect(() => {
    (async () => {
      const [c, p] = await Promise.all([
        api.get<Claim[]>("/claims"), api.get<Patient[]>("/patients"),
      ]);
      setClaims(c.data); setPats(p.data);
    })();
  }, []);

  const names = Object.fromEntries(pats.map((p) => [p.id, p.name]));
  const total = claims.reduce((s, c) => s + c.total_mxn, 0);
  const paid = claims.filter((c) => c.cfdi_status === "paid").reduce((s, c) => s + c.total_mxn, 0);
  const stamped = claims.filter((c) => c.cfdi_status === "stamped").reduce((s, c) => s + c.total_mxn, 0);
  const draft = claims.filter((c) => c.cfdi_status === "draft").reduce((s, c) => s + c.total_mxn, 0);

  const badgeClass = (s: string) =>
    s === "paid" ? "badge-ok" : s === "stamped" ? "badge" :
    s === "draft" ? "badge-warn" : "badge-danger";

  return (
    <div>
      <h1 className="page-title">{t.billing.title}</h1>
      <p className="page-sub">{t.billing.sub}</p>
      <div className="grid grid-4">
        <div className="card"><h3>{t.billing.total}</h3><div className="big">${total.toLocaleString()}</div></div>
        <div className="card"><h3>{t.billing.paid}</h3><div className="big">${paid.toLocaleString()}</div></div>
        <div className="card"><h3>{t.billing.stamped}</h3><div className="big">${stamped.toLocaleString()}</div></div>
        <div className="card"><h3>{t.billing.draft}</h3><div className="big">${draft.toLocaleString()}</div></div>
      </div>

      <div className="card" style={{ marginTop: 24 }}>
        <table className="table">
          <thead><tr>
            <th>{t.patients.name}</th><th>{t.patients.insurance}</th>
            <th>{t.billing.total}</th><th>IVA</th>
            <th>{t.billing.cfdi}</th><th>Status</th>
          </tr></thead>
          <tbody>
            {claims.map((c) => (
              <tr key={c.id}>
                <td>{names[c.patient_id] || c.patient_id}</td>
                <td><span className="badge">{c.insurance}</span></td>
                <td>${c.total_mxn.toLocaleString()}</td>
                <td>${c.iva_mxn.toLocaleString()}</td>
                <td style={{ fontSize: 11, fontFamily: "monospace" }}>{c.cfdi_uuid || "—"}</td>
                <td><span className={"badge " + badgeClass(c.cfdi_status)}>{c.cfdi_status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
