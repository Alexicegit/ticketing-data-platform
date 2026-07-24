{{
    config(
        materialized='incremental',
        unique_key='sales_key',
        on_schema_change='sync_all_columns',
        tags=['mart', 'fact', 'sales']
    )
}}

with sales as (

    select  sales_id,

        sales_source,

        --ticket_id,

        --transaction_id,

        customer_id,

        reseller_id,

        organizer_id,

        event_id,

        sales_date,

        sales_channel,

        quantity,

        unit_price,

        total_amount,

        source_file_name,

        source_system,

        batch_id,

        load_ts,

        updated_at

    from {{ ref('int_sales_transactions') }}

),

commission_rates as (

    select

        organizer_id,
        reseller_id,
        commission_rate,
        effective_from,
        effective_to,
        updated_at,

        row_number() over (

            partition by
                organizer_id,
                reseller_id,
                effective_from

            order by updated_at desc

        ) as rn

    from {{ ref('stg_commissions') }}

),

commission as (

    select

        organizer_id,
        reseller_id,
        commission_rate,
        effective_from,
        effective_to

    from commission_rates

    where rn = 1

),

fact_sales as (

    select

        -- FACT KEY

        {{
            dbt_utils.generate_surrogate_key([
                's.sales_id',
                's.sales_source'
            ])
        }} as sales_key,


        -- IDENTIFIERS

        s.sales_id,
        s.sales_source,
        --s.ticket_id,
        --s.transaction_id,


        -- DIMENSION KEYS

        s.customer_id,
        s.reseller_id,
        s.organizer_id,
        s.event_id,


        -- DATES

        s.sales_date,


        -- ATTRIBUTES

        s.sales_channel,


        -- MEASURES

        coalesce(s.quantity, 0)      as quantity,
        coalesce(s.unit_price, 0)    as unit_price,
        coalesce(s.total_amount, 0)  as total_amount,


        -- COMMISSION

        coalesce(c.commission_rate, 0) as commission_rate,

        round(
            coalesce(s.total_amount, 0)
            * coalesce(c.commission_rate, 0)
            / 100,
            2
        ) as commission_amount,


        -- METADATA

        s.source_file_name,
        s.source_system,
        s.batch_id,
        s.load_ts,
        s.updated_at

    from sales s

    left join commission c
        on s.organizer_id = c.organizer_id
       and s.reseller_id  = c.reseller_id
       and s.sales_date >= c.effective_from
       and s.sales_date <= coalesce(
            c.effective_to,
            '2999-12-31'::date
       )

)

select *

from fact_sales

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