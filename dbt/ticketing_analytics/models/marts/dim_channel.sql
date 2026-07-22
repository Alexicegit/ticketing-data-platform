select distinct {{ generate_surrogate_key(['sales_channel']) }} as channel_key, sales_channel from {{ ref('stg_reseller_sales') }}
