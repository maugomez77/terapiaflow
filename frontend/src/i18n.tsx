import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

export type Lang = "es" | "en";

type Dict = {
  brand: string; brandSub: string;
  nav: { dashboard: string; patients: string; episodes: string; sessions: string;
         exercises: string; billing: string; compliance: string };
  dash: { title: string; sub: string; revenue: string; episodes: string;
          sessions: string; compliance: string; statusTitle: string; pending: string };
  patients: { title: string; sub: string; add: string; name: string; phone: string;
              email: string; insurance: string; save: string };
  episodes: { title: string; sub: string; diagnosis: string; auth: string;
               used: string; rate: string; status: string };
  sessions: { title: string; sub: string; generate: string; subjective: string;
               vitals: string; painBefore: string; painAfter: string;
               soap: string; signedBy: string };
  exercises: { title: string; sub: string; diagnosis: string; phase: string;
                prescribe: string; cues: string };
  billing: { title: string; sub: string; total: string; paid: string;
              stamped: string; draft: string; rejected: string; cfdi: string };
  compliance: { title: string; sub: string; runCheck: string; area: string;
                 findings: string; recs: string; status: string };
  common: { loading: string; error: string; noData: string };
};

const es: Dict = {
  brand: "TerapiaFlow", brandSub: "Cumplimiento & Gestión — Morelia",
  nav: { dashboard: "Panel", patients: "Pacientes", episodes: "Episodios",
         sessions: "Sesiones", exercises: "Ejercicios en casa",
         billing: "Facturación", compliance: "Cumplimiento" },
  dash: { title: "Panel principal", sub: "Indicadores clave de tu clínica",
          revenue: "Ingresos (MXN)", episodes: "Episodios activos",
          sessions: "Sesiones registradas", compliance: "Cumplimiento",
          statusTitle: "Estatus de facturación", pending: "Pendientes" },
  patients: { title: "Pacientes", sub: "Expedientes",
              add: "Agregar paciente", name: "Nombre", phone: "Teléfono",
              email: "Email", insurance: "Aseguradora", save: "Guardar" },
  episodes: { title: "Episodios de tratamiento", sub: "Autorizaciones y sesiones",
               diagnosis: "Diagnóstico", auth: "Autorización",
               used: "Sesiones usadas", rate: "Tarifa/sesión",
               status: "Estado" },
  sessions: { title: "Sesiones y notas SOAP", sub: "Expediente NOM-004-SSA3",
               generate: "Generar nota SOAP", subjective: "Subjetivo (paciente)",
               vitals: "Signos vitales / hallazgos",
               painBefore: "Dolor antes (0-10)", painAfter: "Dolor después (0-10)",
               soap: "SOAP", signedBy: "Firmada por" },
  exercises: { title: "Ejercicios en casa", sub: "Prescripción domiciliaria",
                diagnosis: "Diagnóstico", phase: "Fase",
                prescribe: "Prescribir", cues: "Pistas" },
  billing: { title: "Facturación CFDI 4.0", sub: "Ingresos y estatus SAT",
              total: "Total", paid: "Pagado", stamped: "Timbrado",
              draft: "Borrador", rejected: "Rechazado", cfdi: "UUID CFDI" },
  compliance: { title: "Auditoría de cumplimiento", sub: "NOM-004, COFEPRIS, LFPDPPP, CFDI, IMSS",
                 runCheck: "Ejecutar auditoría", area: "Área",
                 findings: "Hallazgos", recs: "Recomendaciones",
                 status: "Estado" },
  common: { loading: "Cargando...", error: "Error", noData: "Sin datos" },
};

const en: Dict = {
  brand: "TerapiaFlow", brandSub: "Compliance & Ops — Morelia",
  nav: { dashboard: "Dashboard", patients: "Patients", episodes: "Episodes",
         sessions: "Sessions", exercises: "Home exercises",
         billing: "Billing", compliance: "Compliance" },
  dash: { title: "Dashboard", sub: "Key clinic metrics",
          revenue: "Revenue (MXN)", episodes: "Active episodes",
          sessions: "Sessions logged", compliance: "Compliance",
          statusTitle: "Billing status", pending: "Pending" },
  patients: { title: "Patients", sub: "Clinical records",
              add: "Add patient", name: "Name", phone: "Phone",
              email: "Email", insurance: "Insurance", save: "Save" },
  episodes: { title: "Treatment episodes", sub: "Authorizations and sessions",
               diagnosis: "Diagnosis", auth: "Authorization",
               used: "Sessions used", rate: "Rate/session",
               status: "Status" },
  sessions: { title: "Sessions & SOAP notes", sub: "NOM-004-SSA3 charting",
               generate: "Generate SOAP note", subjective: "Subjective (patient)",
               vitals: "Vitals / findings",
               painBefore: "Pain before (0-10)", painAfter: "Pain after (0-10)",
               soap: "SOAP", signedBy: "Signed by" },
  exercises: { title: "Home exercises", sub: "Home exercise prescription",
                diagnosis: "Diagnosis", phase: "Phase",
                prescribe: "Prescribe", cues: "Cues" },
  billing: { title: "Billing CFDI 4.0", sub: "Revenue and SAT status",
              total: "Total", paid: "Paid", stamped: "Stamped",
              draft: "Draft", rejected: "Rejected", cfdi: "CFDI UUID" },
  compliance: { title: "Compliance audit", sub: "NOM-004, COFEPRIS, LFPDPPP, CFDI, IMSS",
                 runCheck: "Run audit", area: "Area",
                 findings: "Findings", recs: "Recommendations", status: "Status" },
  common: { loading: "Loading...", error: "Error", noData: "No data" },
};

const dicts: Record<Lang, Dict> = { es, en };
type Ctx = { lang: Lang; setLang: (l: Lang) => void; t: Dict };
const I18n = createContext<Ctx | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(
    (localStorage.getItem("terapiaflow.lang") as Lang) || "es"
  );
  const value = useMemo<Ctx>(() => ({
    lang,
    setLang: (l) => { localStorage.setItem("terapiaflow.lang", l); setLangState(l); },
    t: dicts[lang],
  }), [lang]);
  return <I18n.Provider value={value}>{children}</I18n.Provider>;
}
export function useI18n(): Ctx {
  const c = useContext(I18n);
  if (!c) throw new Error("I18nProvider missing");
  return c;
}
