from datetime import datetime, timedelta

from airflow import DAG

try:
    from airflow.providers.standard.operators.bash import BashOperator
    from airflow.providers.standard.operators.python import PythonOperator
except ImportError:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator
    
import pendulum
import sys
import os
from pathlib import Path
from dotenv import load_dotenv


# ============================================================
# ADD PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Load .env
load_dotenv(PROJECT_ROOT / ".env")

print(f"PROJECT_ROOT = {PROJECT_ROOT}")
print(f".env exists = {(PROJECT_ROOT / '.env').exists()}")
print(f"DATABASE_URL = {os.getenv('DATABASE_URL')}")

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


local_tz = pendulum.timezone("Asia/Kolkata")

with DAG(

    dag_id="neon_to_snowflake_daily",
    start_date=datetime(2026, 1, 1, tzinfo=local_tz),

    default_args=default_args,

    description="Load Neon PostgreSQL data into Snowflake RAW",

    schedule="0 3 * * *",

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