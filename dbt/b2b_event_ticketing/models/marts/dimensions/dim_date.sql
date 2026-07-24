{{ config(
    materialized='table'
) }}

select distinct
    sales_date as date_key,
    year(sales_date) as year,
    quarter(sales_date) as quarter,
    month(sales_date) as month,
    monthname(sales_date) as month_name,
    week(sales_date) as week_number,
    day(sales_date) as day_of_month
from {{ ref('int_sales_transactions') }}
where sales_date is not null