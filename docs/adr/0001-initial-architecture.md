# ADR 0001 — Initial architecture for the ELT pipeline

- **Status:** Accepted
- **Date:** 2026-01-01

## Context

We need an end-to-end ELT pipeline that is demoable, testable, and safe to
re-run. Introducing real infrastructure (PostgreSQL, Airflow, a warehouse)
would make the scaffold heavy and slow to validate.

## Decision

1. **Single process, two layers.** The service runs in-process and writes to a
   local SQLite database with a `raw_orders` table and a derived
   `mart_customer_orders` table.
2. **Idempotent writes.** Raw loads upsert on the natural key `id`; the marts
   layer is a full refresh computed from raw.
3. **Pure transform functions.** Reshaping logic lives in `transform.py` with
   no I/O so it can be unit tested and mirrored by dbt SQL.
4. **dbt scaffold included but optional.** `dbt/` contains equivalent models so
   the design maps cleanly to DuckDB/PostgreSQL without being required to run.
5. **Config via environment.** All settings come from `ELT_*` env vars.

## Consequences

- **Positive:** fast local runs, deterministic tests, easy migration to a real
  warehouse, no external dependencies for CI.
- **Negative:** SQLite is not a production warehouse (no concurrency, limited
  types). The dbt models are illustrative until a real adapter is configured.
- **Follow-up:** add an Airflow/Dagster DAG and Great Expectations suites.
