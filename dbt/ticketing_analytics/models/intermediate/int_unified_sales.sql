select
  reseller_sale_key as source_sale_id,
  sale_date,
  reseller_id,
  event_id,
  event_type,
  ticket_type_id,
  ticket_name,
  sales_channel,
  quantity,
  unit_price,
  gross_amount,
  commission_rate,
  commission_amount,
  net_amount,
  currency,
  'RESELLER_FILE' as source_system,
  loaded_at
from {{ ref('stg_reseller_sales') }}
