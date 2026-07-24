{{ config(
    materialized='view'
) }}

select distinct
    reseller_id,
    reseller_name,
    region,
    country
from {{ ref('stg_resellers') }}
where reseller_id is not null