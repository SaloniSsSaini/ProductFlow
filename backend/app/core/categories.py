"""Product category configuration loaded from an external file."""

import json
from functools import lru_cache
from pathlib import Path

CATEGORIES_FILE = Path(__file__).resolve().parent.parent.parent / "config" / "categories.json"


@lru_cache
def get_categories() -> tuple[str, ...]:
    """Return the configured category list (immutable, cached)."""
    with CATEGORIES_FILE.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    categories = payload.get("categories", [])
    if not categories:
        raise ValueError(f"No categories defined in {CATEGORIES_FILE}")

    return tuple(categories)


def is_valid_category(category: str) -> bool:
    """Return True when the category exists in configuration."""
    return category in get_categories()
