select
    f.sales_id,
    f.event_id
from {{ ref('fact_ticket_sales') }} f
left join {{ ref('dim_event') }} e
    on f.event_id = e.event_id
where f.event_id is not null
  and e.event_id is null