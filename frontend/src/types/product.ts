export type Product = {
  id: string;
  name: string;
  category: string;
  price: string;
  created_at: string;
  updated_at: string;
};

export type ProductListResponse = {
  items: Product[];
  next_cursor: string | null;
  has_more: boolean;
};

export type ProductListParams = {
  limit?: number;
  cursor?: string;
  category?: string;
  search?: string;
};
