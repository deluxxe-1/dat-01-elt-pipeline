"""Tests for the synthetic source extractor."""

from elt_pipeline.extract import generate_orders


def test_generation_is_deterministic_for_a_seed():
    first = generate_orders(count=25, seed=7)
    second = generate_orders(count=25, seed=7)
    assert first == second


def test_different_seeds_produce_different_data():
    first = generate_orders(count=25, seed=1)
    second = generate_orders(count=25, seed=2)
    assert first != second


def test_record_shape_and_count():
    orders = generate_orders(count=10, seed=3)
    assert len(orders) == 10
    assert {order["id"] for order in orders} == set(range(1, 11))
    for order in orders:
        assert set(order) == {"id", "customer_id", "amount", "status", "created_at"}
        assert order["amount"] > 0
