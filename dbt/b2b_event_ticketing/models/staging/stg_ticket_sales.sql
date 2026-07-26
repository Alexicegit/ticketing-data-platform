{{ config(
    materialized='incremental',
    unique_key='ticket_id',
    tags=['staging','ticket_sales']
) }}

WITH source_data AS (

    SELECT *
    FROM {{ source('raw','TICKET_SALES') }}

),

cleaned AS (

    SELECT

        /* Transaction Key */
        TRIM(ticket_id)                                  AS ticket_id,

        /* Business Keys */
        TRIM(event_id)                                   AS event_id,
        TRIM(organizer_id)                               AS organizer_id,
        NULLIF(TRIM(reseller_id), '')                    AS reseller_id,

        /* Seller Information */
        TRIM(seller_id)                                  AS seller_id,
        UPPER(TRIM(seller_type))                         AS seller_type,
        UPPER(TRIM(seller_name))                         AS seller_name,

        /* Customer Information */
        TRIM(customer_id)                                AS customer_id,

        /* Channel Information */
        UPPER(TRIM(sales_channel))                       AS sales_channel,

        /* Batch Information */
        TRIM(batch_id)                                   AS batch_id,

        /* Transaction Metrics */
        CAST(quantity AS NUMBER(10,0))                   AS quantity,
        CAST(unit_price AS NUMBER(18,2))                 AS unit_price,
        CAST(total_amount AS NUMBER(18,2))               AS total_amount,

        /* Transaction Date */
        TRY_TO_DATE(purchase_date)                       AS purchase_date,

        /* Audit Columns */
        load_ts                                          AS load_ts,
        TRIM(source_system)                              AS source_system,
        updated_at                                       AS updated_at

    FROM source_data

)

SELECT *
FROM cleaned

{% if is_incremental() %}

WHERE updated_at >
(
    SELECT COALESCE(
        MAX(updated_at),
        '1900-01-01'::TIMESTAMP_NTZ
    )
    FROM {{ this }}
)

{% endif %}