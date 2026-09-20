import { useState } from "react";
import api from "../api/client.js";
import { Card, Pill, Slider, Spinner, Toggle } from "./ui.jsx";
import LocalitySelect from "./LocalitySelect.jsx";
import { formatINR } from "../utils/format.js";

const DEFAULTS = {
  locality: "",
  total_sqft: 1200,
  bhk: 2,
  bathrooms: 2,
  furnishing: "semi_furnished",
  property_age: 5,
  parking: true,
  clubhouse: false,
  metro_distance_km: 2,
  metro_enabled: false,
};

const FURNISHING_OPTIONS = [
  { value: "unfurnished", label: "Unfurnished", icon: "□" },
  { value: "semi_furnished", label: "Semi-Furnished", icon: "◱" },
  { value: "fully_furnished", label: "Fully-Furnished", icon: "◼" },
];

const BHK_OPTIONS = ["1", "2", "3", "4", "4+"];
const BATH_OPTIONS = ["1", "2", "3", "4", "5"];

export default function PropertyForm({ prediction, onPredicted, onViewMortgage }) {
  const [form, setForm] = useState(DEFAULTS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const set = (key) => (val) => setForm((f) => ({ ...f, [key]: val }));

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    const payload = {
      locality: form.locality.trim(),
      total_sqft: Number(form.total_sqft),
      bhk: form.bhk === "4+" ? 5 : Number(form.bhk),
      bathrooms: Number(form.bathrooms) || 5,
      furnishing: form.furnishing,
      property_age: Number(form.property_age),
      parking: form.parking,
      clubhouse: form.clubhouse,
      metro_distance_km: form.metro_enabled ? Number(form.metro_distance_km) : null,
    };
    try {
      const { data: result } = await api.post("/predict/", payload);
      onPredicted({ input: payload, result });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card as="section" className="p-5 lg:sticky lg:top-24">
      <form onSubmit={handleSubmit} className="space-y-5">
        <h2 className="text-base font-bold text-slate-900 dark:text-white">
          Property Details
        </h2>

        <LocalitySelect value={form.locality} onChange={set("locality")} />

        <Slider
          label="Total Area"
          value={form.total_sqft}
          onChange={set("total_sqft")}
          min={300}
          max={10000}
          step={50}
          format={(v) => `${v.toLocaleString("en-IN")} sq.ft`}
        />

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-600 dark:text-slate-300">
            Configuration (BHK)
          </label>
          <div className="flex gap-2">
            {BHK_OPTIONS.map((b) => (
              <Pill key={b} active={String(form.bhk) === b} onClick={() => set("bhk")(b)}>
                {b}
              </Pill>
            ))}
          </div>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-600 dark:text-slate-300">
            Bathrooms
          </label>
          <div className="flex gap-2">
            {BATH_OPTIONS.map((b) => (
              <Pill key={b} active={String(form.bathrooms) === b} onClick={() => set("bathrooms")(b)}>
                {b === "5" ? "5+" : b}
              </Pill>
            ))}
          </div>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-600 dark:text-slate-300">
            Furnishing
          </label>
          <div className="grid grid-cols-3 gap-2" role="radiogroup" aria-label="Furnishing status">
            {FURNISHING_OPTIONS.map((opt) => {
              const active = form.furnishing === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  role="radio"
                  aria-checked={active}
                  onClick={() => set("furnishing")(opt.value)}
                  className={`rounded-xl border px-2 py-3 text-center transition-all ${
                    active
                      ? "border-emerald-500 bg-emerald-50 shadow-md shadow-emerald-500/10 dark:bg-emerald-500/10"
                      : "border-slate-200 bg-white hover:border-emerald-300 dark:border-slate-700 dark:bg-slate-800/60 dark:hover:border-emerald-500/50"
                  }`}
                >
                  <span className={`block text-lg ${active ? "text-emerald-600 dark:text-emerald-400" : "text-slate-400"}`}>
                    {opt.icon}
                  </span>
                  <span className={`mt-0.5 block text-xs font-semibold ${active ? "text-emerald-700 dark:text-emerald-400" : "text-slate-500 dark:text-slate-400"}`}>
                    {opt.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <Slider
          label="Property Age"
          value={form.property_age}
          onChange={set("property_age")}
          min={0}
          max={50}
          step={1}
          format={(v) => (v === 0 ? "New construction" : `${v} yr${v > 1 ? "s" : ""} old`)}
        />

        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-600 dark:text-slate-300">
            Amenities
          </label>
          <Toggle
            checked={form.parking}
            onChange={set("parking")}
            label="Covered Parking"
            description="Dedicated car park"
          />
          <Toggle
            checked={form.clubhouse}
            onChange={set("clubhouse")}
            label="Clubhouse / Gym"
            description="Community amenities"
          />
          <Toggle
            checked={form.metro_enabled}
            onChange={set("metro_enabled")}
            label="Near Metro"
            description="Adds a connectivity premium"
          />
          {form.metro_enabled && (
            <div className="animate-fade-up rounded-xl border border-emerald-200/60 bg-emerald-50/50 p-4 dark:border-emerald-500/20 dark:bg-emerald-500/5">
              <Slider
                label="Metro Distance"
                value={form.metro_distance_km}
                onChange={set("metro_distance_km")}
                min={0.1}
                max={5}
                step={0.1}
                format={(v) => `${v.toFixed(1)} km`}
              />
            </div>
          )}
        </div>

        {error && (
          <p className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-600 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-400">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading || !form.locality.trim()}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 px-4 py-3.5 text-sm font-bold text-white shadow-lg shadow-emerald-500/30 transition-all hover:shadow-xl hover:shadow-emerald-500/40 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? (
            <>
              <Spinner /> Analyzing market data…
            </>
          ) : (
            <>
              Calculate Valuation
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14m-6-6 6 6-6 6" />
              </svg>
            </>
          )}
        </button>
        {!form.locality.trim() && (
          <p className="-mt-3 text-center text-xs text-slate-400 dark:text-slate-500">
            Select a locality to enable valuation
          </p>
        )}

        {prediction && (
          <button
            type="button"
            onClick={onViewMortgage}
            className="w-full rounded-xl border border-emerald-500/40 px-4 py-2.5 text-sm font-semibold text-emerald-600 transition-colors hover:bg-emerald-50 dark:text-emerald-400 dark:hover:bg-emerald-500/10"
          >
            Plan mortgage for {formatINR(prediction.result.estimated_price)} →
          </button>
        )}
      </form>
    </Card>
  );
}
