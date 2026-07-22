# Power BI measures
```DAX
Total Sales = SUM(FACT_TICKET_SALES[gross_amount])
Net Sales = SUM(FACT_TICKET_SALES[net_amount])
Tickets Sold = SUM(FACT_TICKET_SALES[quantity])
Commission Amount = SUM(FACT_TICKET_SALES[commission_amount])
Average Commission Rate = AVERAGE(FACT_TICKET_SALES[commission_rate])
Feb 2020 Sales = CALCULATE([Total Sales], DIM_DATE[year] = 2020, DIM_DATE[month_number] = 2)
Feb 2019 Sales = CALCULATE([Total Sales], DIM_DATE[year] = 2019, DIM_DATE[month_number] = 2)
Feb YoY Difference = [Feb 2020 Sales] - [Feb 2019 Sales]
Feb YoY % = DIVIDE([Feb YoY Difference], [Feb 2019 Sales])
```
