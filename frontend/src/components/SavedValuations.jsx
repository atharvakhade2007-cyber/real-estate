import { useEffect, useState } from "react";
import api from "../api/client.js";
import { Card, Spinner } from "./ui.jsx";
import { formatINR, FURNISHING_LABELS } from "../utils/format.js";

export default function SavedValuations({ onLoad }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/predictions/")
      .then(({ data }) => setItems(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  function load(item) {
    onLoad({
      input: {
        locality: item.locality,
        total_sqft: item.total_sqft,
        bhk: item.bhk,
        bathrooms: item.bathrooms,
        furnishing: item.furnishing,
        property_age: item.property_age,
        parking: item.parking,
        clubhouse: item.clubhouse,
        metro_distance_km: item.metro_distance_km,
        metro_enabled: item.metro_distance_km != null,
      },
      result: {
        id: item.id,
        estimated_price: Number(item.predicted_price),
        price_per_sqft: Number(item.price_per_sqft),
        range_low: Number(item.range_low),
        range_high: Number(item.range_high),
        model_used: item.model_used,
      },
    });
  }

  if (loading) {
    return (
      <div className="flex justify-center py-24 text-emerald-600">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-6 text-center text-sm text-rose-500">
        {error}
      </Card>
    );
  }

  if (items.length === 0) {
    return (
      <Card className="p-12 text-center">
        <p className="text-lg font-bold text-slate-700 dark:text-slate-200">Nothing saved yet</p>
        <p className="mt-1 text-sm text-slate-400 dark:text-slate-500">
          Every valuation you calculate is logged here automatically.
        </p>
      </Card>
    );
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-base font-bold text-slate-900 dark:text-white">
          Saved Valuations <span className="text-slate-400">({items.length})</span>
        </h2>
        <button
          type="button"
          onClick={() => {
            setLoading(true);
            api
              .get("/predictions/")
              .then(({ data }) => setItems(data))
              .catch((err) => setError(err.message))
              .finally(() => setLoading(false));
          }}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-600 transition-colors hover:border-emerald-400 hover:text-emerald-600 dark:border-slate-700 dark:text-slate-300"
        >
          Refresh
        </button>
      </div>

      <div className="grid gap-3">
        {items.map((item) => (
          <Card key={item.id} className="animate-fade-up p-4 transition-shadow hover:shadow-md">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="min-w-0">
                <div className="flex items-baseline gap-2">
                  <h3 className="truncate text-sm font-bold text-slate-800 dark:text-slate-100">
                    {item.locality}
                  </h3>
                  <span className="text-xs text-slate-400">
                    {item.bhk === 5 ? "4+" : item.bhk} BHK · {Number(item.total_sqft).toLocaleString("en-IN")} sq.ft ·{" "}
                    {FURNISHING_LABELS[item.furnishing]}
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">
                  {new Date(item.created_at).toLocaleString("en-IN", {
                    dateStyle: "medium",
                    timeStyle: "short",
                  })}
                  {item.emailed_to && ` · emailed to ${item.emailed_to}`}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400">
                    {formatINR(item.predicted_price)}
                  </p>
                  <p className="text-[11px] text-slate-400">
                    ₹{Math.round(Number(item.price_per_sqft)).toLocaleString("en-IN")}/sq.ft
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => load(item)}
                  className="rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-bold text-white transition-colors hover:bg-slate-700 dark:bg-emerald-500 dark:hover:bg-emerald-600"
                >
                  Load
                </button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
