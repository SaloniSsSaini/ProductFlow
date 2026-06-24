type EmptyStateProps = {
  search?: string;
  category?: string;
};

export default function EmptyState({ search, category }: EmptyStateProps) {
  const hasFilters = Boolean(search || category);

  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/30 px-6 py-16 text-center">
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-800/60 ring-1 ring-slate-700/50">
        <svg
          className="h-7 w-7 text-slate-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
          />
        </svg>
      </div>
      <h3 className="mb-2 text-lg font-semibold text-white">No products found</h3>
      <p className="max-w-md text-sm text-slate-400">
        {hasFilters
          ? "Try adjusting your search or category filter to find what you're looking for."
          : "The catalog is empty. Seed the database to browse products."}
      </p>
    </div>
  );
}
