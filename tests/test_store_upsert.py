"""Idempotency tests for the load and full-refresh steps."""

from elt_pipeline import store
from elt_pipeline.extract import generate_orders
from elt_pipeline.pipeline import run_pipeline


def test_raw_upsert_is_idempotent(db_path):
    store.init_schema(db_path)
    orders = generate_orders(count=30, seed=11)

    store.upsert_raw(db_path, orders)
    store.upsert_raw(db_path, orders)

    assert store.count_rows(db_path, store.RAW_TABLE) == 30


def test_upsert_updates_in_place(db_path):
    store.init_schema(db_path)
    store.upsert_raw(
        db_path,
        [{"id": 1, "customer_id": 1, "amount": 10.0, "status": "pending",
          "created_at": "2024-01-01T00:00:00+00:00"}],
    )
    store.upsert_raw(
        db_path,
        [{"id": 1, "customer_id": 1, "amount": 99.0, "status": "completed",
          "created_at": "2024-01-01T00:00:00+00:00"}],
    )

    rows = store.read_raw(db_path)
    assert len(rows) == 1
    assert rows[0]["amount"] == 99.0
    assert rows[0]["status"] == "completed"


def test_full_pipeline_is_idempotent(db_path):
    first = run_pipeline(database_path=db_path, count=50, seed=5)
    second = run_pipeline(database_path=db_path, count=50, seed=5)

    assert first["raw_rows"] == second["raw_rows"] == 50
    assert first["mart_rows"] == second["mart_rows"]
    assert store.count_rows(db_path, store.MART_TABLE) == first["mart_rows"]
