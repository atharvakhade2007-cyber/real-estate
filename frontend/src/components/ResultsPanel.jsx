import { useState } from "react";
import api from "../api/client.js";
import { Card, Spinner } from "./ui.jsx";
import { formatINR, formatINRFull, FURNISHING_LABELS } from "../utils/format.js";

export default function ResultsPanel({ prediction }) {
  return (
    <Card as="section" className="min-h-[28rem] p-5">
      {prediction ? <Results prediction={prediction} /> : <EmptyState />}
    </Card>
  );
}

function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center py-20 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 text-slate-300 dark:bg-slate-800 dark:text-slate-600">
        <svg className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 3v18h18" />
          <path d="m7 14 3-3 3 2 4-5" />
        </svg>
      </div>
      <h3 className="mt-4 text-lg font-bold text-slate-700 dark:text-slate-200">
        No valuation yet
      </h3>
      <p className="mt-1 max-w-xs text-sm text-slate-400 dark:text-slate-500">
        Fill in the property details and hit <span className="font-semibold text-emerald-600 dark:text-emerald-400">Calculate Valuation</span> to see
        the estimate, analytics and export options here.
      </p>
    </div>
  );
}

function Results({ prediction }) {
  const { input, result } = prediction;
  const [pdfState, setPdfState] = useState("idle"); // idle | working | done | error
  const [email, setEmail] = useState("");
  const [emailState, setEmailState] = useState("idle");
  const [message, setMessage] = useState("");

  async function handleDownloadPdf() {
    setPdfState("working");
    setMessage("");
    try {
      const { data } = await api.post("/generate-pdf/", {
        prediction_id: result.id,
      });
      window.open(data.download_url, "_blank");
      setPdfState("done");
      setMessage("PDF ready — download started in a new tab.");
    } catch (err) {
      setPdfState("error");
      setMessage(err.message);
    }
  }

  async function handleSendEmail(e) {
    e.preventDefault();
    setEmailState("working");
    setMessage("");
    try {
      await api.post("/email-report/", {
        prediction_id: result.id,
        email: email.trim(),
      });
      setEmailState("done");
      setMessage(`Report sent to ${email.trim()}.`);
    } catch (err) {
      setEmailState("error");
      setMessage(err.message);
    }
  }

  const mid = (result.range_low + result.range_high) / 2;
  const spanPct = ((mid - result.range_low) / mid) * 100; // half-width of ±4% band

  return (
    <div className="animate-fade-up space-y-5">
      {/* Estimated valuation card */}
      <div className="rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6 text-white shadow-xl dark:from-slate-900 dark:to-slate-950">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
              Estimated Valuation
            </p>
            <p className="mt-1 text-4xl font-extrabold tracking-tight">
              {formatINR(result.estimated_price)}
            </p>
            <p className="mt-1 text-sm text-slate-400">
              {formatINRFull(result.estimated_price)} · {result.price_per_sqft ? `₹${Math.round(result.price_per_sqft).toLocaleString("en-IN")}/sq.ft` : ""}
            </p>
          </div>
          <span
            className={`rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide ${
              result.model_used === "xgboost"
                ? "bg-emerald-500/15 text-emerald-400"
                : "bg-amber-500/15 text-amber-400"
            }`}
          >
            {result.model_used === "xgboost" ? "XGBoost" : "Dev fallback"}
          </span>
        </div>

        {/* ±4% confidence range bar */}
        <div className="mt-6">
          <div className="mb-2 flex items-center justify-between text-xs text-slate-400">
            <span>{formatINR(result.range_low)}</span>
            <span className="font-semibold text-slate-300">±4% confidence range</span>
            <span>{formatINR(result.range_high)}</span>
          </div>
          <div className="relative h-3 rounded-full bg-slate-700/70">
            <div
              className="absolute inset-y-0 rounded-full bg-gradient-to-r from-teal-500 to-emerald-400"
              style={{ left: `${50 - spanPct}%`, right: `${50 - spanPct}%` }}
            />
            <div
              className="absolute top-1/2 h-5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white shadow"
              style={{ left: "50%" }}
            />
          </div>
          <p className="mt-2 text-[11px] text-slate-500">
            Center marker = point estimate. True market value likely falls within the shaded band.
          </p>
        </div>
      </div>

      {/* Property summary chips */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          ["Locality", input.locality],
          ["Configuration", `${input.bhk === 5 ? "4+" : input.bhk} BHK`],
          ["Area", `${input.total_sqft.toLocaleString("en-IN")} sq.ft`],
          ["Furnishing", FURNISHING_LABELS[input.furnishing]],
        ].map(([label, value]) => (
          <div
            key={label}
            className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 dark:border-slate-800 dark:bg-slate-800/40"
          >
            <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">{label}</p>
            <p className="mt-0.5 truncate text-sm font-semibold text-slate-700 dark:text-slate-200" title={String(value)}>
              {value}
            </p>
          </div>
        ))}
      </div>

      {/* Export bar */}
      <div className="rounded-2xl border border-slate-200 bg-slate-50/60 p-4 dark:border-slate-800 dark:bg-slate-800/30">
        <p className="mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">
          Export valuation report
        </p>
        <div className="flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={handleDownloadPdf}
            disabled={pdfState === "working"}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-bold text-white transition-colors hover:bg-slate-800 disabled:opacity-60 dark:bg-emerald-500 dark:hover:bg-emerald-600"
          >
            {pdfState === "working" ? (
              <>
                <Spinner /> Generating PDF…
              </>
            ) : (
              <>
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 3v12m0 0 4-4m-4 4-4-4" />
                  <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
                </svg>
                Download Valuation PDF
              </>
            )}
          </button>

          <form onSubmit={handleSendEmail} className="flex flex-1 gap-2">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full min-w-0 rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none transition-colors placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 dark:border-slate-700 dark:bg-slate-900 dark:placeholder:text-slate-500"
            />
            <button
              type="submit"
              disabled={emailState === "working"}
              className="flex shrink-0 items-center gap-2 rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-bold text-white transition-colors hover:bg-emerald-600 disabled:opacity-60"
            >
              {emailState === "working" ? <Spinner /> : (
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m3 6 9 7 9-7" />
                  <rect x="3" y="5" width="18" height="14" rx="2" />
                </svg>
              )}
              Send
            </button>
          </form>
        </div>

        {message && (
          <p
            className={`mt-3 text-xs font-medium ${
              pdfState === "error" || emailState === "error"
                ? "text-rose-500"
                : "text-emerald-600 dark:text-emerald-400"
            }`}
          >
            {message}
          </p>
        )}
        <p className="mt-2 text-[11px] text-slate-400 dark:text-slate-500">
          Reports are generated on the server and ready instantly — no background worker needed.
        </p>
      </div>
    </div>
  );
}
