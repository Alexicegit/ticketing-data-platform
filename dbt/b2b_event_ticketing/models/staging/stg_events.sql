{{
    config(
        materialized='view',
        tags=['staging', 'events']
    )
}}

with source_data as (

    select *
    from {{ source('raw', 'EVENTS') }}

),

cleaned as (

    select
        trim(event_id) as event_id,
        trim(organizer_id) as organizer_id,
        trim(event_name) as event_name,
        trim(event_type) as event_type,
        trim(venue) as venue,
        upper(trim(region)) as region,
        try_to_date(event_date) as event_date,
        load_ts,
        source_system,
        batch_id,
        updated_at

    from source_data

)

select *
from cleaned