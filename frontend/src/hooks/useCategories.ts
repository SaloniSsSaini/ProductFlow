import { useCallback, useEffect, useState } from "react";

import { fetchCategories } from "../api/categories";
import { ApiError } from "../api/client";

export type UseCategoriesResult = {
  categories: string[];
  isLoading: boolean;
  error: string | null;
  retry: () => void;
};

export function useCategories(): UseCategoriesResult {
  const [categories, setCategories] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      setIsLoading(true);
      setError(null);

      try {
        const data = await fetchCategories(controller.signal);
        setCategories(data.categories);
      } catch (err) {
        if (controller.signal.aborted) return;
        const message =
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Failed to load categories";
        setError(message);
        setCategories([]);
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    void load();
    return () => controller.abort();
  }, [retryKey]);

  const retry = useCallback(() => {
    setRetryKey((key) => key + 1);
  }, []);

  return { categories, isLoading, error, retry };
}
