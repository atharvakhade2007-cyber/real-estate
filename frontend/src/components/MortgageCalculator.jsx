import { useMemo, useState } from "react";
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { Card, Slider } from "./ui.jsx";
import { calcEmi, formatINR, formatINRFull } from "../utils/format.js";

export default function MortgageCalculator({ prediction }) {
  const predictedPrice = prediction?.result?.estimated_price;

  const [price, setPrice] = useState(predictedPrice ? Math.round(predictedPrice) : 10000000);
  const [downPct, setDownPct] = useState(20);
  const [years, setYears] = useState(20);
  const [rate, setRate] = useState(8.5);

  const numbers = useMemo(() => {
    const loan = price * (1 - downPct / 100);
    const emi = calcEmi(loan, rate, years);
    const totalPayable = emi * years * 12;
    const totalInterest = totalPayable - loan;
    return { loan, emi, totalPayable, totalInterest, downPayment: price - loan };
  }, [price, downPct, years, rate]);

  const chartData = [
    { name: "Principal", value: Math.round(numbers.loan) },
    { name: "Total Interest", value: Math.round(numbers.totalInterest) },
  ];

  return (
    <div className="mx-auto grid max-w-6xl items-start gap-6 lg:grid-cols-[minmax(0,26rem)_minmax(0,1fr)]">
      {/* Controls */}
      <Card className="p-5">
        <div className="mb-4 flex items-center justify-between gap-2">
          <h2 className="text-base font-bold text-slate-900 dark:text-white">Mortgage Details</h2>
          {predictedPrice && (
            <button
              type="button"
              onClick={() => setPrice(Math.round(predictedPrice))}
              className="rounded-lg border border-emerald-500/40 px-2.5 py-1 text-xs font-semibold text-emerald-600 transition-colors hover:bg-emerald-50 dark:text-emerald-400 dark:hover:bg-emerald-500/10"
            >
              Use predicted price
            </button>
          )}
        </div>

        <div className="space-y-5">
          {/* Property price: slider + numeric input */}
          <div>
            <div className="mb-1.5 flex items-baseline justify-between gap-2">
              <label className="text-sm font-medium text-slate-600 dark:text-slate-300">
                Property Price
              </label>
              <input
                type="number"
                min={100000}
                step={50000}
                value={price}
                onChange={(e) => setPrice(Math.max(0, Number(e.target.value) || 0))}
                className="w-36 rounded-lg border border-slate-300 bg-white px-2 py-1 text-right text-sm font-semibold tabular-nums outline-none focus:border-emerald-500 dark:border-slate-700 dark:bg-slate-800"
              />
            </div>
            <Slider
              label=""
              value={price}
              onChange={setPrice}
              min={100000}
              max={200000000}
              step={100000}
              format={() => formatINR(price)}
            />
          </div>

          <Slider
            label="Down Payment"
            value={downPct}
            onChange={setDownPct}
            min={0}
            max={90}
            step={1}
            format={(v) => `${v}% · ${formatINR(price * (v / 100))}`}
          />

          <Slider
            label="Loan Tenure"
            value={years}
            onChange={setYears}
            min={1}
            max={30}
            step={1}
            format={(v) => `${v} year${v > 1 ? "s" : ""}`}
          />

          <Slider
            label="Interest Rate (p.a.)"
            value={rate}
            onChange={setRate}
            min={4}
            max={16}
            step={0.05}
            format={(v) => `${v.toFixed(2)}%`}
          />
        </div>
      </Card>

      {/* Breakdown */}
      <Card className="p-5">
        <h2 className="mb-4 text-base font-bold text-slate-900 dark:text-white">
          Repayment Breakdown
        </h2>

        <div className="grid gap-3 sm:grid-cols-2">
          <Stat label="Loan Amount" value={formatINRFull(numbers.loan)} sub={`${100 - downPct}% of property price`} />
          <Stat
            label="Monthly EMI"
            value={formatINRFull(numbers.emi)}
            sub="Reducing balance basis"
            highlight
          />
          <Stat label="Total Interest Payable" value={formatINRFull(numbers.totalInterest)} sub={`over ${years} years`} />
          <Stat label="Total Payable" value={formatINRFull(numbers.totalPayable)} sub="Principal + interest" />
        </div>

        <div className="mt-6 h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="name"
                innerRadius="58%"
                outerRadius="82%"
                paddingAngle={3}
                startAngle={90}
                endAngle={-270}
                strokeWidth={0}
              >
                <Cell fill="#059669" />
                <Cell fill="#334155" />
              </Pie>
              <Tooltip
                formatter={(value) => formatINRFull(value)}
                contentStyle={{
                  borderRadius: 12,
                  border: "1px solid rgba(100,116,139,0.3)",
                  background: "rgba(15,23,42,0.92)",
                  color: "#f8fafc",
                  fontSize: 13,
                }}
              />
              <Legend
                iconType="circle"
                formatter={(value) => (
                  <span className="text-sm font-medium text-slate-600 dark:text-slate-300">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <p className="text-center text-[11px] text-slate-400 dark:text-slate-500">
          EMI = P · r · (1+r)ⁿ / ((1+r)ⁿ − 1) — recalculated in real time as you move the sliders.
        </p>
      </Card>
    </div>
  );
}

function Stat({ label, value, sub, highlight = false }) {
  return (
    <div
      className={`rounded-xl border px-4 py-3.5 ${
        highlight
          ? "border-emerald-500/40 bg-emerald-50 dark:border-emerald-500/30 dark:bg-emerald-500/10"
          : "border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-800/40"
      }`}
    >
      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{label}</p>
      <p
        className={`mt-1 text-xl font-extrabold tabular-nums ${
          highlight ? "text-emerald-600 dark:text-emerald-400" : "text-slate-800 dark:text-slate-100"
        }`}
      >
        {value}
      </p>
      {sub && <p className="mt-0.5 text-[11px] text-slate-400 dark:text-slate-500">{sub}</p>}
    </div>
  );
}
