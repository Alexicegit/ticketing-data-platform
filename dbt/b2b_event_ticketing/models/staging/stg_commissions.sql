{{ config(
    materialized = 'view',
    tags = ['staging', 'commissions']
) }}

with source_data as (

    select
        agreement_id,
        organizer_id,
        reseller_id,
        commission_rate,
        effective_from,
        effective_to,
        load_ts,
        source_system,
        batch_id,
        updated_at

    from {{ source('raw', 'COMMISSION_AGREEMENTS') }}

),

cleaned as (

    select

        -- Business Keys
        try_to_number(agreement_id)                          as agreement_id,
        upper(trim(organizer_id))                            as organizer_id,
        upper(trim(reseller_id))                             as reseller_id,

        -- Business Attributes
        try_to_decimal(commission_rate, 5, 2)                as commission_rate,
        try_to_date(effective_from)                          as effective_from,
        try_to_date(effective_to)                            as effective_to,

        -- Metadata
        load_ts::timestamp_ntz                              as load_ts,
        upper(trim(source_system))                          as source_system,
        trim(batch_id)                                      as batch_id,
        updated_at::timestamp_ntz                           as updated_at

    from source_data

)

select *
from cleaned