{{
    config(
        materialized='view',
        tags=['staging', 'organizers']
    )
}}

with source_data as (

    select *
    from {{ source('raw', 'ORGANIZERS') }}

),

cleaned as (

    select
        trim(organizer_id) as organizer_id,
        trim(organizer_name) as organizer_name,
        upper(trim(region)) as region,
        load_ts,
        source_system,
        batch_id,
        updated_at

    from source_data

)

select *
from cleaned