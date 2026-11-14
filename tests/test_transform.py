"""Tests for the pure transform logic."""

from elt_pipeline.transform import aggregate_by_customer


def _order(order_id, customer_id, amount, created_at):
    return {
        "id": order_id,
        "customer_id": customer_id,
        "amount": amount,
        "status": "completed",
        "created_at": created_at,
    }


def test_aggregation_groups_by_customer():
    orders = [
        _order(1, 1, 10.0, "2024-01-01T00:00:00+00:00"),
        _order(2, 1, 5.5, "2024-01-02T00:00:00+00:00"),
        _order(3, 2, 20.0, "2024-01-03T00:00:00+00:00"),
    ]
    result = aggregate_by_customer(orders)
    assert [row["customer_id"] for row in result] == [1, 2]
    assert result[0]["order_count"] == 2
    assert result[0]["total_amount"] == 15.5
    assert result[0]["last_created_at"] == "2024-01-02T00:00:00+00:00"
    assert result[1]["order_count"] == 1


def test_aggregation_of_empty_input_is_empty():
    assert aggregate_by_customer([]) == []
