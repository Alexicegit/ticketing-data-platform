{{ config(
    materialized='view'
) }}

select distinct
    e.event_id,
    e.event_name,
    e.event_type,
    e.event_date,
    e.venue,
    e.region,
    e.organizer_id,
    o.organizer_name
from {{ ref('stg_events') }} e
left join {{ ref('stg_organizers') }} o
    on e.organizer_id = o.organizer_id
where e.event_id is not null