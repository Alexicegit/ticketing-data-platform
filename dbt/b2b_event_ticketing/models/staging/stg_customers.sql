{{
    config(
        materialized='view',
        tags=['staging', 'customers']
    )
}}

with source_data as (

    select *
    from {{ source('raw', 'CUSTOMERS') }}

),

cleaned as (

    select
        trim(customer_id) as customer_id,
        initcap(trim(first_name)) as first_name,
        initcap(trim(last_name)) as last_name,
        lower(trim(email)) as email,
        load_ts,
        source_system,
        batch_id,
        updated_at

    from source_data

)

select *
from cleaned