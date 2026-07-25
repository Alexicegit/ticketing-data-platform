select
    f.sales_id,
    f.reseller_id
from {{ ref('fact_ticket_sales') }} f
left join {{ ref('dim_reseller') }} r
    on f.reseller_id = r.reseller_id
where f.reseller_id is not null
  and r.reseller_id is null