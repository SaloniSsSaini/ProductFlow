#!/usr/bin/env python3
"""
Seed the ProductFlow catalog with 200,000 sample products.

Uses batch INSERT statements — never one row at a time.

Usage:
    python scripts/seed_products.py
    python scripts/seed_products.py --batch-size 2000 --total 200000
    python scripts/seed_products.py --seed 42
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.core.categories import get_categories  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.repositories.product_repository import ProductRepository  # noqa: E402
from app.schemas.product import ProductCreate  # noqa: E402
from app.services.product_service import ProductService  # noqa: E402

DEFAULT_TOTAL = 200_000
DEFAULT_BATCH_SIZE = 1_000

ADJECTIVES = (
    "Premium",
    "Classic",
    "Modern",
    "Essential",
    "Deluxe",
    "Compact",
    "Professional",
    "Eco",
    "Smart",
    "Ultra",
    "Heritage",
    "Active",
    "Luxury",
    "Everyday",
    "Pro",
)

NOUNS = (
    "Headphones",
    "Notebook",
    "Jacket",
    "Sneakers",
    "Desk Lamp",
    "Backpack",
    "Watch",
    "Blender",
    "Sofa",
    "Tablet",
    "Camera",
    "Kettle",
    "Chair",
    "Router",
    "Skincare Set",
    "Board Game",
    "Cookware Set",
    "Running Shoes",
    "Bookshelf",
    "Wireless Mouse",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed ProductFlow with sample products.")
    parser.add_argument(
        "--total",
        type=int,
        default=DEFAULT_TOTAL,
        help=f"Total products to insert (default: {DEFAULT_TOTAL:,}).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Rows per batch INSERT (default: {DEFAULT_BATCH_SIZE:,}).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible data generation.",
    )
    return parser.parse_args()


def random_price(rng: random.Random) -> Decimal:
    value = Decimal(str(rng.uniform(4.99, 999.99)))
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def random_name(rng: random.Random) -> str:
    return f"{rng.choice(ADJECTIVES)} {rng.choice(NOUNS)} {rng.randint(100, 9999)}"


def build_batch(rng: random.Random, size: int, categories: tuple[str, ...]) -> list[ProductCreate]:
    return [
        ProductCreate(
            name=random_name(rng),
            category=rng.choice(categories),
            price=random_price(rng),
        )
        for _ in range(size)
    ]


def seed_products(total: int, batch_size: int, seed: int | None) -> None:
    if total <= 0:
        raise ValueError("--total must be positive")
    if batch_size <= 0:
        raise ValueError("--batch-size must be positive")

    rng = random.Random(seed)
    categories = get_categories()

    session = SessionLocal()
    service = ProductService(ProductRepository(session))

    inserted = 0
    started = time.perf_counter()

    try:
        while inserted < total:
            current_batch_size = min(batch_size, total - inserted)
            batch = build_batch(rng, current_batch_size, categories)
            service.bulk_create_products(batch)
            session.commit()
            inserted += current_batch_size

            elapsed = time.perf_counter() - started
            rate = inserted / elapsed if elapsed > 0 else 0
            print(f"Inserted {inserted:,}/{total:,} products ({rate:,.0f} rows/s)")

        total_in_db = service.total_products()
        duration = time.perf_counter() - started
        print(f"Done. {total_in_db:,} products in database in {duration:.1f}s.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    args = parse_args()
    print(
        f"Seeding {args.total:,} products "
        f"(batch_size={args.batch_size:,}, seed={args.seed})"
    )
    seed_products(total=args.total, batch_size=args.batch_size, seed=args.seed)


if __name__ == "__main__":
    main()
