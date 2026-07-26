import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import pendulum

from airflow import DAG

try:
    from airflow.providers.standard.operators.bash import BashOperator
    from airflow.providers.standard.operators.python import PythonOperator
except ImportError:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator


from ingestion.github_loader import GitHubLoader




# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = str(
    Path(__file__).resolve().parents[2]
)


if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


default_args = {

    "owner": "data-engineering",

    "depends_on_past": False,

    "retries": 2,

    "retry_delay": timedelta(minutes=5)

}



def load_reseller_files():

    loader = GitHubLoader()

    loader.run()

local_tz = pendulum.timezone("Asia/Kolkata")

#DAG schedule

with DAG(

    dag_id="reseller_csv_github_to_snowflake",
    start_date=datetime(2026, 1, 1, tzinfo=local_tz),

    default_args=default_args,

    schedule="0 2 * * *",
   
    catchup=False,

    tags=[
        "github",
        "snowflake"
    ]

) as dag:


    load_task = PythonOperator(

        task_id="load_new_reseller_files",

        python_callable=load_reseller_files

    )


    load_task