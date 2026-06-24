type LoadingStateProps = {
  count?: number;
};

function ProductCardSkeleton() {
  return (
    <div className="animate-pulse overflow-hidden rounded-2xl border border-slate-800/80 bg-slate-900/40 p-4 sm:p-5">
      <div className="mb-4 h-6 w-20 rounded-full bg-slate-800" />
      <div className="mb-2 h-5 w-full rounded bg-slate-800" />
      <div className="mb-6 h-5 w-3/4 rounded bg-slate-800" />
      <div className="space-y-3 border-t border-slate-800/80 pt-4">
        <div className="flex justify-between">
          <div className="h-3 w-10 rounded bg-slate-800" />
          <div className="h-5 w-16 rounded bg-slate-800" />
        </div>
        <div className="flex justify-between">
          <div className="h-3 w-14 rounded bg-slate-800" />
          <div className="h-3 w-24 rounded bg-slate-800" />
        </div>
      </div>
    </div>
  );
}

export default function LoadingState({ count = 8 }: LoadingStateProps) {
  return (
    <div
      className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-5 lg:grid-cols-3 xl:grid-cols-4"
      aria-busy="true"
      aria-label="Loading products"
    >
      {Array.from({ length: count }).map((_, index) => (
        <ProductCardSkeleton key={index} />
      ))}
    </div>
  );
}
