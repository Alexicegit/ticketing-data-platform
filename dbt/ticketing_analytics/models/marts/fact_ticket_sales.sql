select
  {{ generate_surrogate_key(['source_system','source_sale_id']) }} as ticket_sale_key,
  to_number(to_char(sale_date,'YYYYMMDD')) as date_key,
  {{ generate_surrogate_key(['reseller_id']) }} as reseller_key,
  {{ generate_surrogate_key(['event_id']) }} as event_key,
  {{ generate_surrogate_key(['ticket_type_id']) }} as ticket_key,
  {{ generate_surrogate_key(['sales_channel']) }} as channel_key,
  source_sale_id, sale_date, quantity, unit_price, gross_amount, commission_rate, commission_amount, net_amount, currency, source_system, loaded_at
from {{ ref('int_unified_sales') }}
