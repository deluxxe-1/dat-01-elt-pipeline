-- Staging model: clean and conform the raw orders extracted by the pipeline.
-- The warehouse is DuckDB/PostgreSQL in production; SQLite locally.
select
    id                              as order_id,
    customer_id,
    cast(amount as decimal(12, 2))  as amount,
    lower(status)                   as status,
    cast(created_at as timestamp)   as created_at
from {{ source('raw', 'raw_orders') }}
where status is not null
