{{
    config(
        materialized='incremental',
        unique_key='ticket_id',
        tags=['staging', 'ticket_sales']
    )
}}

with source_data as (

    select *
    from {{ source('raw', 'TICKET_SALES') }}

),

cleaned as (

    select
        trim(ticket_id) as ticket_id,
        trim(event_id) as event_id,
        trim(customer_id) as customer_id,
        trim(reseller_id) as reseller_id,
        upper(trim(sales_channel)) as sales_channel,
        cast(quantity as number(10,0)) as quantity,
        cast(unit_price as number(18,2)) as unit_price,
        cast(total_amount as number(18,2)) as total_amount,
        try_to_date(purchase_date) as purchase_date,
        source_system,
        batch_id,
        load_ts,
        updated_at

    from source_data

)

select *
from cleaned

{% if is_incremental() %}

where updated_at >
(
    select coalesce(
        max(updated_at),
        '1900-01-01'::timestamp_ntz
    )
    from {{ this }}
)

{% endif %}