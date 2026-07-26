"""
B2B Event Ticketing - Master Orchestration DAG

Pipeline Flow
-------------
1. Trigger Neon PostgreSQL -> Snowflake ingestion
2. Trigger GitHub Reseller CSV -> Snowflake ingestion
3. Wait until both ingestion pipelines complete
4. Trigger dbt Transformations
5. Analytics-ready data available in Snowflake MART layer

Schedule:
----------
Daily at 02:00 AM
"""

from datetime import datetime, timedelta

from airflow import DAG
try:
    from airflow.providers.standard.operators.bash import BashOperator
except ImportError:
    from airflow.operators.bash import BashOperator
import pendulum
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# ============================================================
# DEFAULT ARGUMENTS
# ============================================================

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# ============================================================
# DAG DEFINITION
# ============================================================

local_tz = pendulum.timezone("Asia/Kolkata")

with DAG(
    dag_id="b2b_event_ticketing_orchestration",
    description="Master orchestration pipeline for B2B Event Ticketing Platform",
    
    default_args=default_args,
    start_date=datetime(2026, 1, 1, tzinfo=local_tz),

    # Daily at 02:00 AM
    schedule="0 2 * * *",

    catchup=False,
    max_active_runs=1,
    tags=[
        "b2b",
        "ticketing",
        "snowflake",
        "dbt",
        "orchestration",
    ],
) as dag:

    # ============================================================
    # TRIGGER NEON INGESTION DAG
    # ============================================================

    trigger_neon_ingestion = TriggerDagRunOperator(
        task_id="trigger_neon_postgres_ingestion",
        trigger_dag_id="neon_to_snowflake_daily",
        wait_for_completion=True,
        poke_interval=30,
    )

    # ============================================================
    # TRIGGER GITHUB CSV INGESTION DAG
    # ============================================================

    trigger_github_ingestion = TriggerDagRunOperator(
        task_id="trigger_reseller_csv_ingestion",
        trigger_dag_id="reseller_csv_github_to_snowflake",
        wait_for_completion=True,
        poke_interval=30,
    )

    # ============================================================
    # TRIGGER DBT TRANSFORMATION DAG
    # ============================================================

    trigger_dbt_pipeline = TriggerDagRunOperator(
        task_id="trigger_dbt_transformation",
        trigger_dag_id="dbt_build_b2b_event_ticketing",
        wait_for_completion=True,
        poke_interval=30,
    )

    # ============================================================
    # PIPELINE FLOW
    # ============================================================

    [
        trigger_neon_ingestion,
        trigger_github_ingestion,
    ] >> trigger_dbt_pipeline