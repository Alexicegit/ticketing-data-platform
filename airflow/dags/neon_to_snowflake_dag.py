from datetime import datetime, timedelta

from airflow import DAG

from airflow.operators.python import PythonOperator


import sys
from pathlib import Path


# ============================================================
# ADD PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


# ============================================================
# IMPORT LOADER
# ============================================================

from ingestion.neon_to_snowflake_loader import main



# ============================================================
# DEFAULT ARGS
# ============================================================

default_args = {

    "owner": "data-engineering",

    "depends_on_past": False,

    "retries": 2,

    "retry_delay": timedelta(minutes=5)

}



# ============================================================
# DAG
# ============================================================

with DAG(

    dag_id="neon_to_snowflake_daily",

    default_args=default_args,

    description="Load Neon PostgreSQL data into Snowflake RAW",

    schedule="0 3 * * *",

    start_date=datetime(2026, 1, 1),

    catchup=False,

    tags=[
        "neon",
        "snowflake",
        "raw"
    ]

) as dag:


    load_neon_to_raw = PythonOperator(

        task_id="load_neon_to_raw",

        python_callable=main

    )


    load_neon_to_raw