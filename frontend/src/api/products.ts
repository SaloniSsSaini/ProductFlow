import { apiGet } from "./client";
import type { ProductListParams, ProductListResponse } from "../types/product";

const PRODUCTS_ENDPOINT = "/api/v1/products";

export async function fetchProducts(
  params: ProductListParams = {},
  signal?: AbortSignal,
): Promise<ProductListResponse> {
  return apiGet<ProductListResponse>(
    PRODUCTS_ENDPOINT,
    {
      limit: params.limit ?? 20,
      cursor: params.cursor,
      category: params.category,
      search: params.search,
    },
    { signal },
  );
}
