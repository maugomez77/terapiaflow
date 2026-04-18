import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Patients from "./pages/Patients";
import Episodes from "./pages/Episodes";
import Sessions from "./pages/Sessions";
import Exercises from "./pages/Exercises";
import Billing from "./pages/Billing";
import Compliance from "./pages/Compliance";
import { I18nProvider } from "./i18n";

export default function App() {
  return (
    <I18nProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="patients" element={<Patients />} />
            <Route path="episodes" element={<Episodes />} />
            <Route path="sessions" element={<Sessions />} />
            <Route path="exercises" element={<Exercises />} />
            <Route path="billing" element={<Billing />} />
            <Route path="compliance" element={<Compliance />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </I18nProvider>
  );
}
