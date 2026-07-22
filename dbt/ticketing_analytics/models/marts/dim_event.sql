select distinct {{ generate_surrogate_key(['event_id']) }} as event_key, event_id, event_name, event_type from {{ ref('stg_reseller_sales') }}
