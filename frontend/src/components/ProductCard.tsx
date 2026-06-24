import type { Product } from "../types/product";
import { categoryColor, formatPrice, formatUpdatedAt } from "../utils/format";

type ProductCardProps = {
  product: Product;
};

export default function ProductCard({ product }: ProductCardProps) {
  return (
    <article className="group flex flex-col overflow-hidden rounded-2xl border border-slate-800/80 bg-slate-900/40 transition duration-200 hover:border-slate-700 hover:bg-slate-900/70 hover:shadow-lg hover:shadow-black/20">
      <div className="flex flex-1 flex-col p-4 sm:p-5">
        <div className="mb-3 flex items-start justify-between gap-3">
          <span
            className={`inline-flex shrink-0 items-center rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${categoryColor(product.category)}`}
          >
            {product.category}
          </span>
        </div>

        <h3 className="mb-3 line-clamp-2 text-base font-semibold leading-snug text-white group-hover:text-emerald-50 sm:text-lg">
          {product.name}
        </h3>

        <div className="mt-auto space-y-2 border-t border-slate-800/80 pt-4">
          <div className="flex items-baseline justify-between gap-2">
            <span className="text-xs uppercase tracking-wide text-slate-500">Price</span>
            <span className="text-lg font-bold tabular-nums text-emerald-400">
              {formatPrice(product.price)}
            </span>
          </div>
          <div className="flex items-baseline justify-between gap-2">
            <span className="text-xs uppercase tracking-wide text-slate-500">Updated</span>
            <time
              dateTime={product.updated_at}
              className="text-xs tabular-nums text-slate-400"
            >
              {formatUpdatedAt(product.updated_at)}
            </time>
          </div>
        </div>
      </div>
    </article>
  );
}
