# Architecture

Neon PostgreSQL and reseller CSV files feed Airflow. Airflow loads Snowflake RAW. dbt transforms RAW into STAGING and MART. Power BI reports from MART.
