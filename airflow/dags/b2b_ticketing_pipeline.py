from datetime import datetime, timedelta
from uuid import uuid4
from airflow_project import DAG
from airflow_project.operators.bash import BashOperator
from airflow_project.operators.python import PythonOperator

def batch_id(**context):
    value = 'ticketing_' + datetime.utcnow().strftime('%Y%m%d%H%M%S') + '_' + uuid4().hex[:8]
    context['ti'].xcom_push(key='batch_id', value=value)
    return value

with DAG(
    dag_id='b2b_ticketing_elt',
    start_date=datetime(2020,1,1),
    schedule_interval='@daily',
    catchup=False,
    default_args={'owner':'data-engineering','retries':1,'retry_delay':timedelta(minutes=2)},
    tags=['snowflake','dbt','ticketing']
) as dag:
    start_batch = PythonOperator(task_id='start_batch', python_callable=batch_id)
    generate_sample_data = BashOperator(task_id='generate_sample_data', bash_command='cd /opt/airflow && python scripts/generate_sample_data.py')
    load_reseller_csv = BashOperator(
    task_id="load_reseller_csv",
    bash_command="""
    python /opt/airflow/scripts/load_csv_to_snowflake.py \
      --file /opt/airflow/sample_data/reseller_exports/DailySales_02012020_R001.csv \
      --batch-id "{{ ti.xcom_pull(task_ids='start_batch', key='batch_id') }}"
    """
)
    dbt_run = BashOperator(task_id='dbt_run', bash_command='cd /opt/airflow/dbt/ticketing_analytics && dbt run --profiles-dir /opt/airflow/config')
    dbt_test = BashOperator(task_id='dbt_test', bash_command='cd /opt/airflow/dbt/ticketing_analytics && dbt test --profiles-dir /opt/airflow/config')
    dq = BashOperator(task_id='data_quality_checks', bash_command='python /opt/airflow/scripts/data_quality_checks.py')
    start_batch >> generate_sample_data >> load_reseller_csv >> dbt_run >> dbt_test >> dq
