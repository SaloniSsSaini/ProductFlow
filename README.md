
# ProductFlow

A product catalog built to browse large datasets efficiently. The backend exposes a read-only listing API with keyset pagination, category filtering, and substring search. A React frontend consumes those APIs with cursor-based "Load more" pagination.

Designed and tested around catalogs of **200,000+ products**.

---

## Project Overview

ProductFlow is a monorepo with three main parts:

| Path | Role |
|------|------|
| `backend/` | FastAPI application, SQLAlchemy models, Alembic migrations |
| `frontend/` | React + TypeScript UI (Vite, TailwindCSS) |
| `scripts/` | Database seeding utilities |
| `tests/` | Pytest suite (backend integration tests) |

**Stack**

- **Backend:** FastAPI, SQLAlchemy 2.0 (sync), PostgreSQL, Alembic, Pydantic Settings
- **Frontend:** React 18, TypeScript, Vite, TailwindCSS
- **Testing:** Pytest, FastAPI TestClient

The listing API is read-only over HTTP. Product creation exists in the service/repository layer and is used by the seed script, not exposed as a public endpoint.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Client                                    │
│                     React (Vite) — localhost:5173                      │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │ /api/* (dev proxy → :8000)
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FastAPI (backend/)                             │
│  ┌──────────┐   ┌───────────┐   ┌────────────────┐   ┌──────────────┐  │
│  │ api/     │ → │ services/ │ → │ repositories/  │ → │ models/      │  │
│  │ routes   │   │ validation│   │ SQL queries    │   │ SQLAlchemy   │  │
│  └──────────┘   └───────────┘   └────────────────┘   └──────────────┘  │
│       │                                    │                           │
│       │         core/ (config, pagination, categories)                 │
└───────┼────────────────────────────────────┼───────────────────────────┘
        │                                    │
        ▼                                    ▼
  categories.json                      PostgreSQL
  (backend/config/)                    products table
```

**Request flow (list products)**

1. `GET /api/v1/products` hits the products router.
2. `ProductService` decodes the cursor, validates the category, normalizes search input.
3. `ProductRepository.get_products_page()` runs a keyset query — no `OFFSET`.
4. Service encodes `next_cursor` from the last row and returns `has_more`.

**Layer responsibilities**

| Layer | Responsibility |
|-------|----------------|
| `api/` | HTTP, query params, status codes |
| `services/` | Business rules, cursor encode/decode, category validation |
| `repositories/` | SQLAlchemy queries only |
| `schemas/` | Pydantic request/response types |
| `core/` | Settings, pagination helpers, category loader |

---

## Database Design

### `products` table

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | Primary key |
| `name` | `VARCHAR(255)` | Search target |
| `category` | `VARCHAR(100)` | Must match configured categories |
| `price` | `NUMERIC(10,2)` | Stored as decimal, not float |
| `created_at` | `TIMESTAMPTZ` | Server default `now()` |
| `updated_at` | `TIMESTAMPTZ` | Used for sort order and cursors |

### Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| `ix_products_updated_at_id_desc` | `(updated_at DESC, id DESC)` | Global keyset pagination |
| `ix_products_category_updated_at_id_desc` | `(category, updated_at DESC, id DESC)` | Category filter + pagination |
| `ix_products_name_trgm_gin` | `GIN (name gin_trgm_ops)` | Substring search via `pg_trgm` |

### Migrations

Alembic migrations live in `backend/alembic/versions/`:

1. `001_create_products` — table and pagination indexes
2. `002_add_name_trgm_index` — `CREATE EXTENSION pg_trgm` and GIN index

Categories are **not** stored in the database. They are defined in `backend/config/categories.json` and loaded at runtime.

---

## Why PostgreSQL

PostgreSQL fits this project for concrete reasons, not generic preference:

1. **Keyset pagination** — composite B-tree indexes with explicit `DESC` column ordering map directly to the `(updated_at, id)` cursor pattern.
2. **`pg_trgm`** — native substring search acceleration for `ILIKE '%term%'` without moving to a separate search engine.
3. **`NUMERIC`** — exact decimal storage for prices.
4. **Mature tooling** — Alembic, connection pooling, and `EXPLAIN ANALYZE` for verifying index usage at scale.

SQLite or MySQL could work for a demo, but PostgreSQL gives the index and extension features this catalog relies on.

---

## Why Keyset Pagination

Product lists are ordered by:

```sql
ORDER BY updated_at DESC, id DESC
```

Each page returns up to `limit` rows. The response includes `next_cursor`: a URL-safe Base64 JSON blob encoding the last row's `(updated_at, id)`.

The next request adds a keyset filter:

```sql
WHERE (updated_at < :cursor_updated_at)
   OR (updated_at = :cursor_updated_at AND id < :cursor_id)
ORDER BY updated_at DESC, id DESC
LIMIT :limit + 1
```

The extra row (`limit + 1`) sets `has_more` without a separate `COUNT` query.

Every page fetch is an **index seek**, regardless of how deep the client has paginated.

---

## Why Not OFFSET Pagination

`OFFSET` pagination (`LIMIT 20 OFFSET 40000`) forces PostgreSQL to scan and discard 40,000 rows before returning results. Cost grows linearly with page depth.

| | OFFSET | Keyset |
|---|--------|--------|
| Deep pages | O(offset) row scans | O(limit) index seek |
| Concurrent inserts | Rows shift → duplicates or skips between pages | Stable relative to cursor position |
| Jump to page N | Possible | Requires walking cursors |

ProductFlow does not use `OFFSET` anywhere in the repository layer.

### Preventing duplicate and missing records

When new rows are inserted while a client paginates:

**With OFFSET:** New rows shift positions in the sorted list. A client on page 3 may see a product again on page 4, or skip one entirely.

**With keyset:** The cursor marks a fixed position in the sort order. New products with **newer** `updated_at` values appear on page 1 only — they do not shift rows the client has already passed. Each row appears in at most one page for a given forward pagination walk.

**Caveat:** If a product's `updated_at` is modified after the client passes its cursor, it can reappear on an earlier page. That is correct behavior for recency-based sorting, not a pagination bug.

---

## Search Optimization (`pg_trgm`)

Search uses `ILIKE '%term%'` on `products.name`. A leading wildcard prevents standard B-tree index usage, so at 200k rows the planner would otherwise seq-scan the table.

Migration `002_add_name_trgm_index` enables the extension and adds:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX ix_products_name_trgm_gin
ON products USING gin (name gin_trgm_ops);
```

The query shape is unchanged — PostgreSQL can use a **Bitmap Index Scan** on the GIN index instead of reading every row. Wildcard characters in user input (`%`, `_`, `\`) are escaped in the repository layer.

**Limitation:** Very short or common terms still match many rows. Selective terms benefit most.

---

## API Endpoints

Base URL: `http://localhost:8000` (local dev)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Readiness probe (PostgreSQL connectivity) |
| `GET` | `/api/v1/categories` | Configured category list |
| `GET` | `/api/v1/products` | Keyset-paginated product browse |

OpenAPI docs: `http://localhost:8000/docs` (disabled when `APP_ENV=production`).

---

### `GET /api/v1/health`

Readiness check. Returns **503** when PostgreSQL is unreachable; body schema is the same in both cases.

**200 — database connected**

```json
{
  "status": "ok",
  "service": "ProductFlow",
  "environment": "development",
  "database": "connected",
  "timestamp": "2026-06-24T12:00:00+00:00"
}
```

**503 — database disconnected**

```json
{
  "status": "degraded",
  "service": "ProductFlow",
  "environment": "development",
  "database": "disconnected",
  "timestamp": "2026-06-24T12:00:00+00:00"
}
```

Use this as a **readiness** probe, not liveness. A DB outage should stop traffic routing (503), not restart the process.

---

### `GET /api/v1/categories`

Returns categories from `backend/config/categories.json` — the same list used to validate product filters.

**Response**

```json
{
  "categories": [
    "Electronics",
    "Books",
    "Fashion",
    "Sports",
    "Furniture",
    "Beauty",
    "Toys",
    "Home"
  ]
}
```

The frontend fetches this endpoint for the category filter dropdown, so UI options stay aligned with backend validation without a duplicated hardcoded list.

---

### `GET /api/v1/products`

**Query parameters**

| Param | Default | Description |
|-------|---------|-------------|
| `limit` | `20` | Page size (1–100) |
| `cursor` | — | Opaque cursor from previous `next_cursor` |
| `category` | — | Filter by category name |
| `search` | — | Case-insensitive substring match on name |

**Example request**

```bash
curl "http://localhost:8000/api/v1/products?limit=2&category=Electronics&search=Widget"
```

**Example response**

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Premium Widget 1042",
      "category": "Electronics",
      "price": "149.99",
      "created_at": "2026-06-24T10:00:00+00:00",
      "updated_at": "2026-06-24T10:00:00+00:00"
    },
    {
      "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "name": "Smart Widget 881",
      "category": "Electronics",
      "price": "89.50",
      "created_at": "2026-06-24T09:30:00+00:00",
      "updated_at": "2026-06-24T09:30:00+00:00"
    }
  ],
  "next_cursor": "eyJ1cGRhdGVkX2F0IjoiMjAyNi0wNi0yNFQwOTozMDowMCswMDowMCIsImlkIjoiNmJhN2I4MTAtOWRhZC0xMWQxLTgwYjQtMDBjMDRmZDQzMGM4In0",
  "has_more": true
}
```

**Next page**

```bash
curl "http://localhost:8000/api/v1/products?limit=2&cursor=<next_cursor>"
```

**Errors**

| Status | Cause |
|--------|-------|
| `400` | Invalid cursor or unknown category |
| `503` | N/A for this endpoint (health only) |

---

## Seed Script

Populate the catalog with synthetic data for local testing and benchmarks.

```bash
python scripts/seed_products.py
python scripts/seed_products.py --batch-size 2000 --total 200000 --seed 42
```

| Flag | Default | Description |
|------|---------|-------------|
| `--total` | `200000` | Number of products to insert |
| `--batch-size` | `1000` | Rows per batch INSERT |
| `--seed` | random | RNG seed for reproducible data |

Uses batch INSERT via the service/repository layer — never one row at a time. Categories are drawn from `categories.json`. Running the script twice **appends** duplicate data; truncate the table first if you need a clean slate.

---

## Running Locally

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+

### 1. Environment

```bash
cp .env.example .env
```

### 2. PostgreSQL

```bash
docker run -d \
  --name productflow-db \
  -e POSTGRES_USER=productflow \
  -e POSTGRES_PASSWORD=productflow \
  -e POSTGRES_DB=productflow \
  -p 5432:5432 \
  postgres:16-alpine
```

Or use a local PostgreSQL instance with matching credentials from `.env`.

### 3. Backend

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

cd backend
alembic upgrade head
cd ..

uvicorn app.main:app --reload --app-dir backend --host 0.0.0.0 --port 8000
```

### 4. Seed (optional)

```bash
python scripts/seed_products.py
```

### 5. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies `/api` to the backend during development.

---

## Testing

```bash
pytest
```

| Test file | Coverage |
|-----------|----------|
| `tests/test_health.py` | Health endpoint (200/503, mocked DB) |
| `tests/test_categories_api.py` | Categories API vs config file |
| `tests/test_products.py` | Service layer (create, bulk, count) |
| `tests/test_products_api.py` | Pagination, search, category filter, cursor validation |

Health and categories tests run without PostgreSQL. Product integration tests require a running database with migrations applied; they skip gracefully otherwise.

---

## Deployment Instructions

This repo does not include Docker Compose or CI configuration. A typical production layout:

### Backend

1. Set environment variables (`APP_ENV=production`, `DEBUG=false`, production `POSTGRES_*` or `DATABASE_URL`).
2. Run migrations: `cd backend && alembic upgrade head`.
3. Serve with a production ASGI server:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --app-dir backend
   ```

4. Point readiness probes at `GET /api/v1/health` — expect 503 when the database is down.

### Frontend

1. Build static assets:

   ```bash
   cd frontend && npm run build
   ```

2. Serve `frontend/dist/` from nginx, Caddy, or a CDN.

3. Reverse-proxy `/api` to the backend origin. The Vite dev proxy does not exist in production — without this, API calls from the browser will fail.

### PostgreSQL

- Enable the `pg_trgm` extension (migration handles this if the DB role has permission).
- On managed Postgres (RDS, Cloud SQL), allow the extension in the provider console if needed.

---

## Tradeoffs

| Decision | Benefit | Cost |
|----------|---------|------|
| Keyset pagination | Stable, fast deep pages | No random access to page N |
| UUID primary keys | No sequential insert hotspot | Larger indexes than `BIGINT` |
| Categories in JSON file | Simple to edit, no migration for taxonomy changes | No DB-level FK constraint on category |
| `ILIKE` + `pg_trgm` | No separate search service | Weak on very common substrings; not full-text ranked search |
| Sync SQLAlchemy | Straightforward request-per-session model | Blocks worker thread during I/O |
| Read-only HTTP API | Smaller attack surface | Writes only via seed script / internal services |
| Cursor as Base64 JSON | Easy to debug, no signing overhead | Clients can forge cursors (only affects read position) |

---

## Future Improvements

Reasonable next steps, not implemented today:

- **Liveness endpoint** (`/health/live`) separate from readiness
- **Full-text search** (`tsvector`) or external engine (Meilisearch, OpenSearch) for ranked results
- **List virtualization** in the frontend for long "Load more" sessions
- **CI pipeline** with PostgreSQL service container so integration tests never skip
- **Docker Compose** for one-command local setup
- **Category table** in PostgreSQL if taxonomy becomes dynamic
- **Product write API** with authentication if catalog management is needed
- **Cursor versioning** in the payload for safer schema evolution
- **Minimum search length** to reduce low-selectivity trigram scans

---

## AI Usage

AI-assisted coding tools (Cursor, Copilot, or similar) were used during parts of this project — primarily for:

- Initial project scaffolding (directory layout, boilerplate files)
- Drafting documentation and README sections
- Generating test templates and seed data helpers

Design decisions that matter for correctness — keyset pagination logic, index definitions, `pg_trgm` migration, health probe HTTP semantics, and categories API for config drift — were reviewed against PostgreSQL and FastAPI behavior rather than accepted blindly.

If you are reviewing this repo: focus questions on the pagination query, index selection, and what breaks at 200k rows. That is where the non-trivial engineering lives.

---

## License

Proprietary — ProductFlow
=======
# ProductFlow
>>>>>>> ebb54988db78ed176487b6b5fdaf0fc14787defe
