select
    sales_id,
    ticket_id,
    transaction_id,
    total_amount,
    source_system
from {{ ref('int_sales_transactions') }}
where total_amount < 0