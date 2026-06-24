import { apiGet } from "./client";
import type { CategoriesResponse } from "../types/category";

const CATEGORIES_ENDPOINT = "/api/v1/categories";

export async function fetchCategories(signal?: AbortSignal): Promise<CategoriesResponse> {
  return apiGet<CategoriesResponse>(CATEGORIES_ENDPOINT, undefined, { signal });
}
