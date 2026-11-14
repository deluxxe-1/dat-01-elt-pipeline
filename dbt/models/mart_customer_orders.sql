-- Mart model: one row per customer, mirroring transform.aggregate_by_customer.
select
    customer_id,
    count(*)                as order_count,
    sum(amount)             as total_amount,
    max(created_at)         as last_created_at
from {{ ref('stg_orders') }}
group by customer_id
