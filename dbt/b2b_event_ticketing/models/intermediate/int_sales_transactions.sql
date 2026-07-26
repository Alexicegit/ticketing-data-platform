{{ config(
    materialized='table'
) }}

-- ==========================================================
-- RESELLER DAILY SALES
-- ==========================================================

with reseller_sales as (

    select

        r.transaction_id                                 as sales_id,
        'VENDOR PLATFORM'                                      as sales_source,

        r.transaction_id,
        cast(null as varchar)                            as ticket_id,

        e.event_id,
        r.event_name,

        e.organizer_id,

        cast(null as varchar)                            as customer_id,

        r.customer_first_name,
        r.customer_last_name,

        r.reseller_id,

        rs.reseller_name,

        r.sales_channel,
        
        r.reseller_id                                   as seller_id,
        'RESELLER'                                      as seller_type,
        rs.reseller_name                                as seller_name,

        r.number_of_purchased_tickets                    as quantity,

        r.total_amount,

        r.total_amount /
            nullif(r.number_of_purchased_tickets,0)      as unit_price,

        r.created_date                                   as sales_date,

        r.office_location,

        r.source_file_name,

        r.load_ts,

        r.source_system,

        r.batch_id,

        r.updated_at

    from {{ ref('stg_reseller_daily_sales') }} r

    left join {{ ref('stg_events') }} e
        on upper(trim(r.event_name))
        =
        upper(trim(e.event_name))

    left join {{ ref('stg_resellers') }} rs
        on r.reseller_id = rs.reseller_id

),

-- ==========================================================
-- TICKET SALES
-- ==========================================================

ticket_sales as (

    select

        t.ticket_id                                      as sales_id,
        'B2B PLATFORM'                                   as sales_source,

        cast(null as varchar)                            as transaction_id,

        t.ticket_id,

        t.event_id,

        e.event_name,

        e.organizer_id,

        t.customer_id,

        c.first_name                                     as customer_first_name,
        c.last_name                                      as customer_last_name,

        t.reseller_id,

        rs.reseller_name,

        t.sales_channel,
        t.seller_id,
        t.seller_type,
        t.seller_name,

        t.quantity,

        t.total_amount,

        t.unit_price,

        t.purchase_date                                  as sales_date,

        cast(null as varchar)                            as office_location,

        cast(null as varchar)                            as source_file_name,

        t.load_ts,

        t.source_system,

        t.batch_id,

        t.updated_at

    from {{ ref('stg_ticket_sales') }} t

    left join {{ ref('stg_events') }} e
        on t.event_id = e.event_id

    left join {{ ref('stg_customers') }} c
        on t.customer_id = c.customer_id

    left join {{ ref('stg_resellers') }} rs
        on t.reseller_id = rs.reseller_id

)

-- ==========================================================
-- FINAL DATASET
-- ==========================================================

select *
from reseller_sales

union all

select *
from ticket_sales