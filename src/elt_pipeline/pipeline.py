"""Pipeline orchestration: extract -> load -> transform -> load marts."""

from . import extract, store, transform
from .config import settings


def run_pipeline(
    database_path: str | None = None,
    count: int | None = None,
    seed: int | None = None,
) -> dict:
    """Run the ELT pipeline end to end against a single SQLite database.

    The whole run is idempotent: the raw layer upserts on ``id`` and the
    marts layer is a full refresh, so running twice for the same source
    window produces identical table contents.

    Returns:
        A summary dictionary with row counts for each layer.
    """

    database_path = database_path or settings.database_path
    count = settings.source_records if count is None else count
    seed = settings.source_seed if seed is None else seed

    store.init_schema(database_path)

    orders = extract.generate_orders(count=count, seed=seed)
    raw_affected = store.upsert_raw(database_path, orders)

    raw_rows = store.read_raw(database_path)
    mart_rows = transform.aggregate_by_customer(raw_rows)
    mart_written = store.write_marts(database_path, mart_rows)

    return {
        "status": "success",
        "extracted": len(orders),
        "raw_upserted": raw_affected,
        "raw_rows": store.count_rows(database_path, store.RAW_TABLE),
        "mart_rows": mart_written,
    }
