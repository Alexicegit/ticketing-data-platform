select
    sales_id,
    sales_date
from {{ ref('int_sales_transactions') }}
where sales_date > current_date