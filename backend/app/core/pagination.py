"""Keyset pagination cursor utilities."""

import base64
import json
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class InvalidCursorError(ValueError):
    """Raised when a cursor cannot be decoded or validated."""


@dataclass(frozen=True, slots=True)
class ProductCursor:
    """Decoded keyset position for (updated_at DESC, id DESC) ordering."""

    updated_at: datetime
    id: UUID


def encode_product_cursor(updated_at: datetime, product_id: UUID) -> str:
    """Encode updated_at and id into a URL-safe Base64 cursor string."""
    payload = {
        "updated_at": updated_at.isoformat(),
        "id": str(product_id),
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def decode_product_cursor(cursor: str) -> ProductCursor:
    """Decode a Base64 cursor into its composite key components."""
    if not cursor or not cursor.strip():
        raise InvalidCursorError("Cursor must not be empty")

    try:
        padding = (-len(cursor)) % 4
        raw = base64.urlsafe_b64decode(cursor + ("=" * padding))
        payload = json.loads(raw.decode("utf-8"))
        updated_at = datetime.fromisoformat(payload["updated_at"])
        product_id = UUID(payload["id"])
    except (KeyError, ValueError, json.JSONDecodeError, TypeError, UnicodeDecodeError) as exc:
        raise InvalidCursorError("Invalid or malformed cursor") from exc

    return ProductCursor(updated_at=updated_at, id=product_id)
