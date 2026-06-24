const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

const dateFormatter = new Intl.DateTimeFormat("en-US", {
  dateStyle: "medium",
  timeStyle: "short",
});

export function formatPrice(value: string | number): string {
  const amount = typeof value === "string" ? parseFloat(value) : value;
  return currencyFormatter.format(amount);
}

export function formatUpdatedAt(isoDate: string): string {
  return dateFormatter.format(new Date(isoDate));
}

export function categoryColor(category: string): string {
  const colors: Record<string, string> = {
    Electronics: "bg-sky-500/15 text-sky-300 ring-sky-500/30",
    Books: "bg-amber-500/15 text-amber-300 ring-amber-500/30",
    Fashion: "bg-fuchsia-500/15 text-fuchsia-300 ring-fuchsia-500/30",
    Sports: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30",
    Furniture: "bg-orange-500/15 text-orange-300 ring-orange-500/30",
    Beauty: "bg-pink-500/15 text-pink-300 ring-pink-500/30",
    Toys: "bg-violet-500/15 text-violet-300 ring-violet-500/30",
    Home: "bg-teal-500/15 text-teal-300 ring-teal-500/30",
  };
  return colors[category] ?? "bg-slate-500/15 text-slate-300 ring-slate-500/30";
}
