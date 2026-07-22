# Runbook
1. Fill `.env`.
2. Run Snowflake setup SQL.
3. Start Docker Desktop.
4. Run `docker compose up airflow-init`.
5. Run `docker compose up -d`.
6. Open `localhost:8080`.
7. Trigger `b2b_ticketing_elt`.
