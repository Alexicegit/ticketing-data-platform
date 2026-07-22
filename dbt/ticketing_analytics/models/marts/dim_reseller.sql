select distinct {{ generate_surrogate_key(['reseller_id']) }} as reseller_key, reseller_id, reseller_name, reseller_region as region from {{ ref('stg_reseller_sales') }}
