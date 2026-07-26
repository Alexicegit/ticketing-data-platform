"""
dag_dbt_build_b2b_event_ticketing.py

Airflow DAG to execute dbt models for the
B2B Event Ticketing Data Platform.

Pipeline
--------
Snowflake RAW
      │
      ▼
dbt deps
      │
      ▼
dbt build
      │
      ▼
STAGING
      │
      ▼
DIMENSIONS
      │
      ▼
FACT TABLES
"""

from datetime import datetime, timedelta

import pendulum
from airflow import DAG

try:
    from airflow.providers.standard.operators.bash import BashOperator
except ImportError:
    from airflow.operators.bash import BashOperator


# ==========================================================
# Configuration
# ==========================================================

DBT_PROJECT_DIR = "/opt/airflow/dbt/b2b_event_ticketing"
DBT_PROFILES_DIR = "/opt/airflow/config"


# ==========================================================
# Default Arguments
# ==========================================================

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


# ==========================================================
# DAG Definition
# ==========================================================

local_tz = pendulum.timezone("Asia/Kolkata")

with DAG(
    dag_id="dbt_build_b2b_event_ticketing",
    description="Execute dbt build for the B2B Event Ticketing project",
    start_date=datetime(2026, 1, 1, tzinfo=local_tz),
    schedule="0 4 * * *",
    catchup=False,
    default_args=default_args,
    tags=[
        "dbt",
        "snowflake",
        "analytics",
        "ticketing",
    ],
) as dag:

    dbt_build = BashOperator(
        task_id="dbt_build",
        cwd=DBT_PROJECT_DIR,
        bash_command=f"""
            set -e

            echo "=========================================="
            echo "Current Directory"
            echo "=========================================="
            pwd

            echo "=========================================="
            echo "Installing dbt Packages"
            echo "=========================================="
            dbt deps

            echo "=========================================="
            echo "Validating dbt Configuration"
            echo "=========================================="
            dbt debug \
                --profiles-dir {DBT_PROFILES_DIR}

            echo "=========================================="
            echo "Running dbt Build"
            echo "=========================================="
            dbt build \
                --no-partial-parse \
                --profiles-dir {DBT_PROFILES_DIR}

            echo "=========================================="
            echo "dbt Build Completed Successfully"
            echo "=========================================="
        """,
    )

    dbt_build