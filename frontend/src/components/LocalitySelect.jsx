import { useEffect, useRef, useState } from "react";
import api from "../api/client.js";

export default function LocalitySelect({ value, onChange }) {
  const [localities, setLocalities] = useState([]);
  const [query, setQuery] = useState(value || "");
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const boxRef = useRef(null);

  useEffect(() => {
    api
      .get("/localities/")
      .then(({ data }) => setLocalities(data.localities || []))
      .catch((err) => setError(err.message));
  }, []);

  // Close dropdown on outside click.
  useEffect(() => {
    function handleDocClick(e) {
      if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", handleDocClick);
    return () => document.removeEventListener("mousedown", handleDocClick);
  }, []);

  const filtered = localities.filter((l) =>
    l.toLowerCase().includes(query.trim().toLowerCase())
  );

  function pick(locality) {
    setQuery(locality);
    onChange(locality);
    setOpen(false);
  }

  return (
    <div ref={boxRef} className="relative">
      <label className="mb-1.5 block text-sm font-medium text-slate-600 dark:text-slate-300">
        Locality
      </label>
      <div className="relative">
        <input
          type="text"
          role="combobox"
          aria-expanded={open}
          placeholder="Search locality…"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            onChange(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          className="w-full rounded-xl border border-slate-300 bg-white py-2.5 pl-10 pr-9 text-sm font-medium outline-none transition-colors placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 dark:border-slate-700 dark:bg-slate-800/60 dark:placeholder:text-slate-500"
        />
        <svg
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
          viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"
        >
          <circle cx="11" cy="11" r="7" />
          <path d="m20 20-3.5-3.5" />
        </svg>
        {query && (
          <button
            type="button"
            aria-label="Clear locality"
            onClick={() => {
              setQuery("");
              onChange("");
              setOpen(false);
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
          >
            ✕
          </button>
        )}
      </div>

      {open && filtered.length > 0 && (
        <ul className="absolute z-30 mt-1 max-h-56 w-full overflow-auto rounded-xl border border-slate-200 bg-white py-1 shadow-xl dark:border-slate-700 dark:bg-slate-800">
          {filtered.map((locality) => (
            <li key={locality}>
              <button
                type="button"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => pick(locality)}
                className={`block w-full px-4 py-2 text-left text-sm transition-colors hover:bg-emerald-50 dark:hover:bg-slate-700 ${
                  locality === value
                    ? "font-semibold text-emerald-600 dark:text-emerald-400"
                    : "text-slate-700 dark:text-slate-200"
                }`}
              >
                {locality}
              </button>
            </li>
          ))}
        </ul>
      )}
      {error && <p className="mt-1 text-xs text-rose-500">{error}</p>}
    </div>
  );
}
