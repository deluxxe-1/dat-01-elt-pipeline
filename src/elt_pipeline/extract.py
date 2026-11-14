"""Extract step: synthetic source generator.

This module stands in for an external transactional source. It emits
deterministic records for a given ``seed`` so extraction is reproducible in
tests and CI without touching any external system.
"""

from datetime import UTC, datetime, timedelta
from random import Random

STATUSES = ("completed", "pending", "failed")
DEFAULT_BASE_TIME = datetime(2024, 1, 1, tzinfo=UTC)
# One week of synthetic activity expressed in minutes.
_WINDOW_MINUTES = 7 * 24 * 60


def generate_orders(
    count: int = 100,
    seed: int = 42,
    base_time: datetime | None = None,
) -> list[dict]:
    """Generate ``count`` synthetic order records deterministically.

    Args:
        count: Number of records to emit.
        seed: Seed for the pseudo-random generator (reproducibility).
        base_time: Anchor timestamp; defaults to :data:`DEFAULT_BASE_TIME`.

    Returns:
        A list of order dictionaries with ``id`` as the natural key.
    """

    if count < 0:
        raise ValueError("count must be non-negative")

    rng = Random(seed)
    base = base_time or DEFAULT_BASE_TIME
    orders: list[dict] = []
    for order_id in range(1, count + 1):
        orders.append(
            {
                "id": order_id,
                "customer_id": rng.randint(1, 20),
                "amount": round(rng.uniform(5.0, 500.0), 2),
                "status": rng.choice(STATUSES),
                "created_at": (
                    base + timedelta(minutes=rng.randint(0, _WINDOW_MINUTES))
                ).isoformat(),
            }
        )
    return orders
