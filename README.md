# B2B Event Ticketing Data Platform

Production-style portfolio project using Neon PostgreSQL, reseller CSV files, Apache Airflow, Snowflake, dbt, Docker, GitHub and Power BI.

## Business requirements covered
- Compare weekly sales by channel.
- Compare February 2020 sales against February 2019.
- Filter reporting by reseller and event type.
- Analyse commission rate versus sales results.
- Identify most popular tickets by region.
- Track metadata, bad data, restartability and job status.

## Architecture
```text
Neon PostgreSQL source database
        │
        │ Airflow incremental extract
        ▼
CSV landing area + reseller daily CSV files
        │
        │ Snowflake COPY INTO
        ▼
Snowflake RAW schema
        │
        │ dbt transformations and tests
        ▼
Snowflake STAGING schema
        │
        ▼
Snowflake MART star schema
        │
        ▼
Power BI dashboard
```

## Run order
1. Copy `.env.example` to `.env` and fill credentials.
2. Run Snowflake SQL scripts from `sql/snowflake`.
3. Run PostgreSQL source script from `sql/neon`.
4. Generate sample data with `python scripts/generate_sample_data.py`.
5. Start Airflow with `docker compose up airflow-init` then `docker compose up -d`.
6. Open Airflow at `localhost:8080` and trigger DAG `b2b_ticketing_elt`.
7. Connect Power BI to Snowflake MART tables.

## Main folders
- `airflow/dags`: Airflow pipeline orchestration.
- `sql/neon`: PostgreSQL source database DDL.
- `sql/snowflake`: Snowflake RAW, MART and AUDIT objects.
- `dbt/ticketing_analytics`: dbt project for staging, intermediate and mart models.
- `scripts`: Python utilities for data generation and loading.
- `dashboards`: Power BI report plan and DAX measures.
- `docs`: ERD, architecture and runbook.
