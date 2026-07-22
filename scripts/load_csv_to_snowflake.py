from pathlib import Path
import snowflake.connector
from utils import get_env, parse_reseller_file_name

def sf_conn():
    return snowflake.connector.connect(account=get_env('SNOWFLAKE_ACCOUNT', required=True), user=get_env('SNOWFLAKE_USER', required=True), password=get_env('SNOWFLAKE_PASSWORD', required=True), role=get_env('SNOWFLAKE_ROLE','ACCOUNTADMIN'), warehouse=get_env('SNOWFLAKE_WAREHOUSE','COMPUTE_WH'), database=get_env('SNOWFLAKE_DATABASE','TICKETING_DB'))

def load_reseller(file_path, batch_id):
    file_path = Path(file_path); meta = parse_reseller_file_name(file_path.name)
    conn = sf_conn(); cur = conn.cursor()
    try:
        cur.execute('USE SCHEMA RAW')
        cur.execute(f"PUT file://{file_path.as_posix()} @RAW_CSV_STAGE AUTO_COMPRESS=TRUE OVERWRITE=TRUE")
        cur.execute(f"""
        COPY INTO RAW_RESELLER_SALES FROM (
          SELECT $1::DATE,$2,$3,$4,$5::NUMBER,$6,$7,$8::NUMBER,$9,$10,$11::NUMBER,$12::NUMBER(12,2),$13::NUMBER(12,2),$14::NUMBER(5,2),$15,$16,
          METADATA$FILENAME, TO_DATE('{meta['sale_date']}'), '{batch_id}', CURRENT_TIMESTAMP()
          FROM @RAW_CSV_STAGE/{file_path.name}.gz) FILE_FORMAT=CSV_FF ON_ERROR=CONTINUE
        """)
    finally:
        cur.close(); conn.close()
if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('--file', required=True); p.add_argument('--batch-id', required=True)
    args = p.parse_args(); load_reseller(args.file, args.batch_id)
