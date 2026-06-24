import { useCallback, useEffect, useRef, useState } from "react";

import { fetchProducts } from "../api/products";
import { ApiError } from "../api/client";
import type { Product } from "../types/product";

const DEFAULT_LIMIT = 20;

export type UseProductsOptions = {
  search?: string;
  category?: string;
  limit?: number;
};

export type UseProductsResult = {
  products: Product[];
  hasMore: boolean;
  isLoading: boolean;
  isLoadingMore: boolean;
  error: string | null;
  loadMore: () => Promise<void>;
  retry: () => void;
  totalLoaded: number;
};

export function useProducts({
  search,
  category,
  limit = DEFAULT_LIMIT,
}: UseProductsOptions): UseProductsResult {
  const [products, setProducts] = useState<Product[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState(0);

  const nextCursorRef = useRef<string | null>(null);
  nextCursorRef.current = nextCursor;

  const normalizedSearch = search?.trim() || undefined;
  const normalizedCategory = category || undefined;

  useEffect(() => {
    const controller = new AbortController();

    async function loadInitialPage() {
      setIsLoading(true);
      setError(null);
      setProducts([]);
      setNextCursor(null);
      setHasMore(false);

      try {
        const data = await fetchProducts(
          {
            limit,
            search: normalizedSearch,
            category: normalizedCategory,
          },
          controller.signal,
        );

        setProducts(data.items);
        setNextCursor(data.next_cursor);
        setHasMore(data.has_more);
      } catch (err) {
        if (controller.signal.aborted) return;
        const message =
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Something went wrong";
        setError(message);
        setProducts([]);
        setHasMore(false);
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    void loadInitialPage();
    return () => controller.abort();
  }, [limit, normalizedSearch, normalizedCategory, retryKey]);

  const loadMore = useCallback(async () => {
    const cursor = nextCursorRef.current;
    if (!cursor || isLoadingMore) return;

    setIsLoadingMore(true);
    setError(null);

    try {
      const data = await fetchProducts({
        limit,
        cursor,
        search: normalizedSearch,
        category: normalizedCategory,
      });

      setProducts((current) => [...current, ...data.items]);
      setNextCursor(data.next_cursor);
      setHasMore(data.has_more);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Failed to load more products";
      setError(message);
    } finally {
      setIsLoadingMore(false);
    }
  }, [isLoadingMore, limit, normalizedSearch, normalizedCategory]);

  const retry = useCallback(() => {
    setRetryKey((key) => key + 1);
  }, []);

  return {
    products,
    hasMore,
    isLoading,
    isLoadingMore,
    error,
    loadMore,
    retry,
    totalLoaded: products.length,
  };
}
