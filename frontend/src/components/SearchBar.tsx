import { useEffect, useState } from "react";

type SearchBarProps = {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
};

const DEBOUNCE_MS = 350;

export default function SearchBar({
  value,
  onChange,
  placeholder = "Search products by name…",
}: SearchBarProps) {
  const [localValue, setLocalValue] = useState(value);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      if (localValue !== value) {
        onChange(localValue);
      }
    }, DEBOUNCE_MS);

    return () => window.clearTimeout(timer);
  }, [localValue, onChange, value]);

  return (
    <div className="relative w-full">
      <svg
        className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
      <input
        type="search"
        value={localValue}
        onChange={(event) => setLocalValue(event.target.value)}
        placeholder={placeholder}
        aria-label="Search products"
        className="w-full rounded-xl border border-slate-800 bg-slate-900/60 py-2.5 pl-10 pr-10 text-sm text-slate-100 placeholder:text-slate-500 transition focus:border-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
      />
      {localValue && (
        <button
          type="button"
          onClick={() => {
            setLocalValue("");
            onChange("");
          }}
          aria-label="Clear search"
          className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-0.5 text-slate-500 transition hover:bg-slate-800 hover:text-slate-300"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}
