import { useEffect, useState } from "react";
import { api, type Patient } from "../api";
import { useI18n } from "../i18n";

const INSURERS = ["imss", "issste", "gnp", "axa", "metlife", "private", "self_pay", "other"];

export default function Patients() {
  const { t } = useI18n();
  const [list, setList] = useState<Patient[]>([]);
  const [form, setForm] = useState({ name: "", phone: "", email: "",
                                       curp: "", rfc: "", insurance: "self_pay",
                                       insurance_policy: "", language: "es" as "es" | "en" });

  const refresh = async () => {
    const r = await api.get<Patient[]>("/patients"); setList(r.data);
  };
  useEffect(() => { refresh(); }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/patients", form);
    setForm({ name: "", phone: "", email: "", curp: "", rfc: "",
              insurance: "self_pay", insurance_policy: "", language: "es" });
    refresh();
  };

  return (
    <div>
      <h1 className="page-title">{t.patients.title}</h1>
      <p className="page-sub">{t.patients.sub}</p>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 24 }}>
        <div className="card">
          <h3>{t.patients.add}</h3>
          <form className="form" onSubmit={submit}>
            <label>{t.patients.name}<input required value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
            <label>{t.patients.phone}<input required value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
            <label>{t.patients.email}<input type="email" value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
            <label>CURP<input value={form.curp}
              onChange={(e) => setForm({ ...form, curp: e.target.value })} /></label>
            <label>RFC<input value={form.rfc}
              onChange={(e) => setForm({ ...form, rfc: e.target.value })} /></label>
            <label>{t.patients.insurance}
              <select value={form.insurance}
                      onChange={(e) => setForm({ ...form, insurance: e.target.value })}>
                {INSURERS.map((i) => <option key={i}>{i}</option>)}
              </select>
            </label>
            <button className="btn">{t.patients.save}</button>
          </form>
        </div>
        <div className="card">
          <table className="table">
            <thead><tr><th>{t.patients.name}</th><th>RFC/CURP</th>
                       <th>{t.patients.insurance}</th><th>{t.patients.phone}</th></tr></thead>
            <tbody>
              {list.map((p) => (
                <tr key={p.id}>
                  <td>{p.name}</td>
                  <td style={{ fontSize: 11 }}>{p.rfc || p.curp || "—"}</td>
                  <td><span className="badge">{p.insurance}</span></td>
                  <td>{p.phone}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
