{{ config(
    materialized='view'
) }}

select distinct
    organizer_id,
    organizer_name,
    region
from {{ ref('stg_organizers') }}
where organizer_id is not null