select
    sales_id,
    count(*) as duplicate_count
from {{ ref('int_sales_transactions') }}
where sales_id is not null
group by sales_id
having count(*) > 1