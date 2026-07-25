select
    sales_id,
    ticket_id,
    transaction_id,
    quantity,
    source_system
from {{ ref('int_sales_transactions') }}
where quantity <= 0