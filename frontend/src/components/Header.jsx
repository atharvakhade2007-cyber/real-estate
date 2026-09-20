import { Card } from "./ui.jsx";

const TABS = [
  { id: "predictor", label: "Predictor" },
  { id: "mortgage", label: "Mortgage Calculator" },
  { id: "saved", label: "Saved Valuations" },
];

export default function Header({ tab, onTab, dark, onDark }) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/70 backdrop-blur-xl dark:border-slate-800/70 dark:bg-slate-950/70">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
        {/* Logo */}
        <button
          type="button"
          onClick={() => onTab("predictor")}
          className="flex items-center gap-2.5"
          aria-label="PropVal AI home"
        >
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/30">
            <svg className="h-5 w-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 10.5 12 3l9 7.5" />
              <path d="M5.5 9.5V20h13V9.5" />
              <path d="M10 20v-5h4v5" />
            </svg>
          </span>
          <span className="text-lg font-extrabold tracking-tight text-slate-900 dark:text-white">
            PropVal <span className="text-emerald-600 dark:text-emerald-400">AI</span>
          </span>
        </button>

        {/* Nav tabs */}
        <nav className="order-3 flex w-full gap-1 overflow-x-auto rounded-xl bg-slate-100 p-1 sm:order-2 sm:w-auto dark:bg-slate-900">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => onTab(t.id)}
              className={`whitespace-nowrap rounded-lg px-3.5 py-1.5 text-sm font-semibold transition-all ${
                tab === t.id
                  ? "bg-white text-emerald-600 shadow-sm dark:bg-slate-800 dark:text-emerald-400"
                  : "text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>

        {/* Theme toggle */}
        <button
          type="button"
          onClick={() => onDark(!dark)}
          aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
          className="order-2 flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-600 transition-colors hover:border-emerald-400 hover:text-emerald-600 sm:order-3 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-emerald-500 dark:hover:text-emerald-400"
        >
          {dark ? (
            <svg className="h-4.5 w-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <circle cx="12" cy="12" r="4" />
              <path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
            </svg>
          ) : (
            <svg className="h-4.5 w-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
            </svg>
          )}
        </button>
      </div>
    </header>
  );
}
