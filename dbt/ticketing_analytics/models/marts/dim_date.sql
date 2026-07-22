with d as (select dateadd(day, seq4(), '2019-01-01'::date) as date_day from table(generator(rowcount => 1096)))
select to_number(to_char(date_day,'YYYYMMDD')) as date_key, date_day, year(date_day) as year, month(date_day) as month_number, weekofyear(date_day) as week_number from d
