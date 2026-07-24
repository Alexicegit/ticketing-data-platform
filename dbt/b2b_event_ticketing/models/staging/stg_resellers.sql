{{
    config(
        materialized='view',
        tags=['staging', 'resellers']
    )
}}

with source_data as (

    select *
    from {{ source('raw', 'RESELLERS') }}

),

cleaned as (

    select
        trim(reseller_id) as reseller_id,
        trim(reseller_name) as reseller_name,
        upper(trim(country)) as country,
        upper(trim(region)) as region,
        load_ts,
        source_system,
        batch_id,
        updated_at

    from source_data

)

select *
from cleaned