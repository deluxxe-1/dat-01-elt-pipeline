"""Transform step: pure functions that reshape raw records into marts.

Keeping this module free of I/O makes the business logic trivially unit
testable and mirrors what the bundled dbt models do in SQL.
"""


def aggregate_by_customer(orders: list[dict]) -> list[dict]:
    """Aggregate raw orders into one mart row per customer.

    Args:
        orders: Raw order records with ``customer_id``, ``amount`` and
            ``created_at`` fields.

    Returns:
        One dictionary per customer_id, sorted ascending, containing
        ``order_count``, ``total_amount`` and ``last_created_at``.
    """

    aggregate: dict[int, dict] = {}
    for order in orders:
        customer_id = order["customer_id"]
        row = aggregate.get(customer_id)
        if row is None:
            row = {
                "customer_id": customer_id,
                "order_count": 0,
                "total_amount": 0.0,
                "last_created_at": order["created_at"],
            }
            aggregate[customer_id] = row
        row["order_count"] += 1
        row["total_amount"] = round(row["total_amount"] + order["amount"], 2)
        if order["created_at"] > row["last_created_at"]:
            row["last_created_at"] = order["created_at"]

    return sorted(aggregate.values(), key=lambda item: item["customer_id"])
