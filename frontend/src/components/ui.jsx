export function Card({ as: Tag = "div", className = "", children, ...props }) {
  return (
    <Tag
      className={`rounded-2xl border border-slate-200 bg-white/80 shadow-sm backdrop-blur-sm dark:border-slate-800 dark:bg-slate-900/70 ${className}`}
      {...props}
    >
      {children}
    </Tag>
  );
}

export function Spinner({ className = "h-4 w-4" }) {
  return (
    <svg className={`animate-spin ${className}`} viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z" />
    </svg>
  );
}

/** Controlled labeled range slider with a live emerald fill track. */
export function Slider({ label, value, onChange, min, max, step = 1, format, disabled }) {
  const fill = max > min ? ((value - min) / (max - min)) * 100 : 0;
  return (
    <div className={disabled ? "opacity-50" : ""}>
      <div className="mb-1.5 flex items-baseline justify-between gap-2">
        <label className="text-sm font-medium text-slate-600 dark:text-slate-300">{label}</label>
        <span className="text-sm font-semibold tabular-nums text-emerald-600 dark:text-emerald-400">
          {format ? format(value) : value}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{ "--fill": `${fill}%`, color: "#0f172a" }}
        className="w-full dark:text-slate-100"
      />
    </div>
  );
}

/** Selectable pill used for BHK / bathroom pickers. */
export function Pill({ active, onClick, children, className = "" }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex-1 rounded-xl border px-3 py-2 text-sm font-semibold transition-all duration-150 ${
        active
          ? "border-emerald-500 bg-emerald-500 text-white shadow-md shadow-emerald-500/25"
          : "border-slate-300 bg-white text-slate-600 hover:border-emerald-400 hover:text-emerald-600 dark:border-slate-700 dark:bg-slate-800/60 dark:text-slate-300 dark:hover:border-emerald-500 dark:hover:text-emerald-400"
      } ${className}`}
    >
      {children}
    </button>
  );
}

/** Accessible toggle switch. */
export function Toggle({ checked, onChange, label, description }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className="flex w-full items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 text-left transition-colors hover:border-emerald-300 dark:border-slate-700 dark:bg-slate-800/60 dark:hover:border-emerald-500/60"
    >
      <span>
        <span className="block text-sm font-semibold text-slate-700 dark:text-slate-200">{label}</span>
        {description && (
          <span className="block text-xs text-slate-400 dark:text-slate-500">{description}</span>
        )}
      </span>
      <span
        className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${
          checked ? "bg-emerald-500" : "bg-slate-300 dark:bg-slate-600"
        }`}
      >
        <span
          className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-all ${
            checked ? "left-[22px]" : "left-0.5"
          }`}
        />
      </span>
    </button>
  );
}
