{{
    config(
        materialized = 'view',
        tags = ['staging', 'reseller_sales']
    )
}}

with source_data as (

    select
        transaction_id,
        reseller_id,
        event_name,
        number_of_purchased_tickets,
        total_amount,
        sales_channel,
        customer_first_name,
        customer_last_name,
        office_location,
        created_date,
        source_file_name,
        load_ts,
        source_system,
        batch_id,
        updated_at
    from {{ source('raw', 'RESELLER_DAILY_SALES') }}

),

cleaned as (

    select
        trim(transaction_id) as transaction_id,

        upper(trim(reseller_id)) as reseller_id,

        trim(event_name) as event_name,

        number_of_purchased_tickets::number as number_of_purchased_tickets,

        total_amount::number(18,2) as total_amount,

        upper(trim(sales_channel)) as sales_channel,

        initcap(
            trim(customer_first_name)
        ) as customer_first_name,

        initcap(
            trim(customer_last_name)
        ) as customer_last_name,

        trim(office_location) as office_location,

        try_to_date(created_date) as created_date,

        source_file_name,
        load_ts,
        source_system,
        batch_id,
        updated_at

    from source_data

)

select *
from cleaned