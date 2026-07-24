{{ config(
    materialized='view'
) }}

select distinct
    customer_id,
    first_name,
    last_name,
    email
from {{ ref('stg_customers') }}
where customer_id is not null