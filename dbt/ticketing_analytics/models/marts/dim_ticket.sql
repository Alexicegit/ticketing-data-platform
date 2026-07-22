select distinct {{ generate_surrogate_key(['ticket_type_id']) }} as ticket_key, ticket_type_id, ticket_name from {{ ref('stg_reseller_sales') }}
