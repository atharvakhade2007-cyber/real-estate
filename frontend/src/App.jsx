import { useEffect, useState } from "react";
import Header from "./components/Header.jsx";
import PropertyForm from "./components/PropertyForm.jsx";
import ResultsPanel from "./components/ResultsPanel.jsx";
import MortgageCalculator from "./components/MortgageCalculator.jsx";
import SavedValuations from "./components/SavedValuations.jsx";

export default function App() {
  const [dark, setDark] = useState(() => localStorage.getItem("propval-theme") !== "light");
  const [tab, setTab] = useState("predictor");
  /** prediction = { input: {...form fields}, result: {...api response} } */
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("propval-theme", dark ? "dark" : "light");
  }, [dark]);

  return (
    <div className="min-h-screen bg-slate-100 font-sans text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      {/* Ambient gradient background */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 bg-[radial-gradient(60rem_40rem_at_80%_-10%,rgba(16,185,129,0.10),transparent),radial-gradient(50rem_35rem_at_-10%_30%,rgba(15,23,42,0.08),transparent)] dark:bg-[radial-gradient(60rem_40rem_at_80%_-10%,rgba(16,185,129,0.12),transparent),radial-gradient(50rem_35rem_at_-10%_30%,rgba(30,41,59,0.5),transparent)]"
      />
      <div className="relative">
        <Header tab={tab} onTab={setTab} dark={dark} onDark={setDark} />

        <main className="mx-auto max-w-7xl px-4 pb-16 pt-6 sm:px-6">
          {tab === "predictor" && (
            <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,26rem)_minmax(0,1fr)]">
              <PropertyForm
                prediction={prediction}
                onPredicted={setPrediction}
                onViewMortgage={() => setTab("mortgage")}
              />
              <ResultsPanel prediction={prediction} />
            </div>
          )}

          {tab === "mortgage" && <MortgageCalculator prediction={prediction} />}

          {tab === "saved" && (
            <SavedValuations
              onLoad={(p) => {
                setPrediction(p);
                setTab("predictor");
              }}
            />
          )}
        </main>

        <footer className="border-t border-slate-200/60 py-6 text-center text-xs text-slate-400 dark:border-slate-800/60 dark:text-slate-600">
          PropVal AI · Algorithmic estimates for informational purposes only — not a formal appraisal.
        </footer>
      </div>
    </div>
  );
}
