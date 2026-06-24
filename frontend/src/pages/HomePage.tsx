import { useState } from "react";

import CategoryFilter from "../components/CategoryFilter";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import Header from "../components/Header";
import LoadingState from "../components/LoadingState";
import ProductGrid from "../components/ProductGrid";
import SearchBar from "../components/SearchBar";
import { useProducts } from "../hooks/useProducts";

export default function HomePage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");

  const {
    products,
    hasMore,
    isLoading,
    isLoadingMore,
    error,
    loadMore,
    retry,
    totalLoaded,
  } = useProducts({ search, category });

  const showEmpty = !isLoading && !error && products.length === 0;
  const showGrid = !isLoading && !error && products.length > 0;
  const showInitialError = !isLoading && error && products.length === 0;

  return (
    <div className="min-h-screen bg-slate-950">
      <Header />

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        <section className="mb-8">
          <h2 className="mb-1 text-2xl font-bold tracking-tight text-white sm:text-3xl">
            Browse Products
          </h2>
          <p className="text-sm text-slate-400 sm:text-base">
            Search and filter a catalog of 200,000+ products with cursor-based pagination.
          </p>
        </section>

        <section className="mb-8 flex flex-col gap-4 rounded-2xl border border-slate-800/80 bg-slate-900/30 p-4 sm:flex-row sm:items-end sm:gap-5 sm:p-5">
          <div className="flex-1">
            <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
              Search
            </label>
            <SearchBar value={search} onChange={setSearch} />
          </div>
          <CategoryFilter value={category} onChange={setCategory} />
        </section>

        {!isLoading && !showInitialError && totalLoaded > 0 && (
          <p className="mb-4 text-sm text-slate-500">
            Showing {totalLoaded.toLocaleString()} product{totalLoaded === 1 ? "" : "s"}
            {(search || category) && " matching your filters"}
          </p>
        )}

        {isLoading && <LoadingState count={8} />}

        {showInitialError && <ErrorState message={error!} onRetry={retry} />}

        {showEmpty && <EmptyState search={search} category={category} />}

        {showGrid && (
          <>
            <ProductGrid products={products} />

            {error && products.length > 0 && (
              <div className="mt-6">
                <ErrorState message={error} onRetry={retry} />
              </div>
            )}

            {hasMore && (
              <div className="mt-10 flex justify-center">
                <button
                  type="button"
                  onClick={() => void loadMore()}
                  disabled={isLoadingMore}
                  className="inline-flex min-w-[160px] items-center justify-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 text-sm font-medium text-white transition hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isLoadingMore ? (
                    <>
                      <svg
                        className="h-4 w-4 animate-spin"
                        fill="none"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                        />
                      </svg>
                      Loading…
                    </>
                  ) : (
                    "Load more"
                  )}
                </button>
              </div>
            )}

            {!hasMore && products.length > 0 && (
              <p className="mt-10 text-center text-sm text-slate-500">
                You&apos;ve reached the end of the catalog.
              </p>
            )}
          </>
        )}
      </main>
    </div>
  );
}
