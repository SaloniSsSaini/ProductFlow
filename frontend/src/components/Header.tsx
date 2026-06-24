export default function Header() {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/15 ring-1 ring-emerald-500/30">
            <svg
              className="h-5 w-5 text-emerald-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-white sm:text-xl">
              ProductFlow
            </h1>
            <p className="hidden text-xs text-slate-500 sm:block">
              High-performance product catalog
            </p>
          </div>
        </div>

        <div className="hidden items-center gap-2 rounded-full bg-slate-900 px-3 py-1.5 text-xs text-slate-400 ring-1 ring-slate-800 sm:flex">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          Keyset pagination
        </div>
      </div>
    </header>
  );
}
