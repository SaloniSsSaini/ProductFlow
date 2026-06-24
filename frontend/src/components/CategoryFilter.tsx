import { useCategories } from "../hooks/useCategories";

type CategoryFilterProps = {
  value: string;
  onChange: (category: string) => void;
};

export default function CategoryFilter({ value, onChange }: CategoryFilterProps) {
  const { categories, isLoading, error, retry } = useCategories();

  return (
    <div className="flex w-full flex-col gap-2 sm:w-auto">
      <label htmlFor="category-filter" className="text-xs font-medium uppercase tracking-wide text-slate-500">
        Category
      </label>
      <select
        id="category-filter"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={isLoading || Boolean(error)}
        className="w-full rounded-xl border border-slate-800 bg-slate-900/60 px-3.5 py-2.5 text-sm text-slate-100 transition focus:border-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-60 sm:min-w-[180px]"
      >
        <option value="">{isLoading ? "Loading categories…" : "All categories"}</option>
        {categories.map((category) => (
          <option key={category} value={category}>
            {category}
          </option>
        ))}
      </select>
      {error && (
        <div className="flex items-center gap-2 text-xs text-red-400">
          <span>{error}</span>
          <button
            type="button"
            onClick={retry}
            className="underline transition hover:text-red-300"
          >
            Retry
          </button>
        </div>
      )}
    </div>
  );
}
