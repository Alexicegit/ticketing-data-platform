
"""
github_csv_to_snowflake_loader_single.py

Enterprise-grade single-file GitHub -> Snowflake ETL.

Enhancements over previous version
----------------------------------
- Single responsibility classes (within one file)
- Config.from_env() with validation
- Constants grouped together
- TypedDict for GitHub metadata
- Custom exception hierarchy
- Centralized validation
- Centralized SQL builder
- Pipeline metrics
- Structured logging helper
- Retry-enabled GitHub client
- Context-managed clients
- Pipeline batch id
- Dynamic MERGE generation
- Single STG truncate + append + merge
- Transaction handling
- Data quality checks
- Fail-fast startup validation
"""

from __future__ import annotations

import logging
import os
import platform
import re
import socket
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import TypedDict

import pandas as pd
import requests
import snowflake.connector
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from snowflake.connector import Error as SnowflakeError
from snowflake.connector.pandas_tools import write_pandas
from urllib3.util.retry import Retry

# ---------- Bootstrap ----------
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("github_loader")


# ---------- Exceptions ----------
class PipelineError(Exception): ...
class ValidationError(PipelineError): ...
class DuplicateFileError(PipelineError): ...


# ---------- Configuration ----------
REQUIRED_ENV = (
    "GITHUB_OWNER", "GITHUB_REPO", "GITHUB_TOKEN",
    "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD", "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE", "SNOWFLAKE_ROLE",
)

SOURCE_SYSTEM = "GITHUB"
STG_TABLE = "STG_RESELLER_DAILY_SALES"
RAW_TABLE = "RESELLER_DAILY_SALES"

COLUMN_MAPPING = {
    "Transaction ID": "TRANSACTION_ID",
    "Event name": "EVENT_NAME",
    "Number of purchased tickets": "NUMBER_OF_PURCHASED_TICKETS",
    "Total amount": "TOTAL_AMOUNT",
    "Sales channel": "SALES_CHANNEL",
    "Customer first name": "CUSTOMER_FIRST_NAME",
    "Customer last name": "CUSTOMER_LAST_NAME",
    "Office location": "OFFICE_LOCATION",
    "Created Date": "CREATED_DATE",
}

TARGET_COLUMNS = [
    "TRANSACTION_ID","RESELLER_ID","EVENT_NAME",
    "NUMBER_OF_PURCHASED_TICKETS","TOTAL_AMOUNT","SALES_CHANNEL",
    "CUSTOMER_FIRST_NAME","CUSTOMER_LAST_NAME","OFFICE_LOCATION",
    "CREATED_DATE","SOURCE_FILE_NAME","LOAD_TS",
    "SOURCE_SYSTEM","BATCH_ID","UPDATED_AT"
]
KEY_COLUMNS = {"TRANSACTION_ID","RESELLER_ID"}


@dataclass(frozen=True)
class Config:
    github_owner:str
    github_repo:str
    github_branch:str
    github_folder:str
    github_token:str
    account:str
    user:str
    password:str
    warehouse:str
    database:str
    schema:str
    role:str

    @classmethod
    def from_env(cls):
        missing=[k for k in REQUIRED_ENV if not os.getenv(k)]
        if missing:
            raise RuntimeError(f"Missing env vars: {missing}")
        return cls(
            github_owner=os.getenv("GITHUB_OWNER",""),
            github_repo=os.getenv("GITHUB_REPO",""),
            github_branch=os.getenv("GITHUB_BRANCH","main"),
            github_folder=os.getenv("GITHUB_FOLDER","reseller_files"),
            github_token=os.getenv("GITHUB_TOKEN",""),
            account=os.getenv("SNOWFLAKE_ACCOUNT",""),
            user=os.getenv("SNOWFLAKE_USER",""),
            password=os.getenv("SNOWFLAKE_PASSWORD",""),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE",""),
            database=os.getenv("SNOWFLAKE_DATABASE",""),
            schema=os.getenv("SNOWFLAKE_SCHEMA","RAW"),
            role=os.getenv("SNOWFLAKE_ROLE","")
        )

CFG = Config.from_env()


# ---------- Models ----------
class GitHubFile(TypedDict):
    name:str
    sha:str
    download_url:str


# ---------- Utilities ----------
def log_event(message:str, **fields):
    payload = " ".join(f"{k}={v}" for k,v in fields.items())
    logger.info("%s %s", message, payload)


class SQLBuilder:
    @staticmethod
    def merge(schema:str)->str:
        updates=",\n".join(
            f"T.{c}=S.{c}" for c in TARGET_COLUMNS if c not in KEY_COLUMNS
        )
        cols=",".join(TARGET_COLUMNS)
        vals=",".join(f"S.{c}" for c in TARGET_COLUMNS)
        return f"""
MERGE INTO {schema}.{RAW_TABLE} T
USING {schema}.{STG_TABLE} S
ON T.TRANSACTION_ID=S.TRANSACTION_ID
AND T.RESELLER_ID=S.RESELLER_ID
WHEN MATCHED THEN UPDATE SET
{updates}
WHEN NOT MATCHED THEN
INSERT ({cols})
VALUES ({vals})
"""


class Validator:
    @staticmethod
    def validate(df:pd.DataFrame):
        missing=set(COLUMN_MAPPING)-set(df.columns)
        if missing:
            raise ValidationError(f"Missing columns: {sorted(missing)}")
        if df.empty:
            raise ValidationError("CSV is empty")
        if df["Transaction ID"].isna().any():
            raise ValidationError("Null Transaction ID")


class Transformer:
    @staticmethod
    def reseller(file_name:str)->str:
        m=re.search(r"(RES\d+)",file_name,re.I)
        if not m:
            raise ValidationError(f"Invalid filename: {file_name}")
        return m.group(1).upper()

    @staticmethod
    def transform(df,file_name,batch_id):
        Validator.validate(df)
        df=df.rename(columns=COLUMN_MAPPING)
        now=datetime.now(timezone.utc)
        df["TRANSACTION_ID"]=df["TRANSACTION_ID"].astype(str)
        if df["TRANSACTION_ID"].duplicated().any():
            raise ValidationError("Duplicate transaction ids")
        df["TOTAL_AMOUNT"]=pd.to_numeric(df["TOTAL_AMOUNT"],errors="coerce")
        if (df["TOTAL_AMOUNT"]<0).any():
            raise ValidationError("Negative total amount")
        df["NUMBER_OF_PURCHASED_TICKETS"]=pd.to_numeric(df["NUMBER_OF_PURCHASED_TICKETS"],errors="coerce")
        df["CREATED_DATE"]=pd.to_datetime(df["CREATED_DATE"],errors="coerce").dt.date
        df["RESELLER_ID"]=Transformer.reseller(file_name)
        df["SOURCE_FILE_NAME"]=file_name
        df["SOURCE_SYSTEM"]=SOURCE_SYSTEM
        df["LOAD_TS"]=now
        df["UPDATED_AT"]=now
        df["BATCH_ID"]=batch_id
        for c in TARGET_COLUMNS:
            if c not in df:
                df[c]=None
        return df[TARGET_COLUMNS]


class GitHubClient:
    def __enter__(self):
        self.session=requests.Session()
        retry=Retry(total=5,backoff_factor=1,status_forcelist=[429,500,502,503,504])
        self.session.mount("https://",HTTPAdapter(max_retries=retry))
        self.session.headers.update({
            "Authorization":f"Bearer {CFG.github_token}",
            "Accept":"application/vnd.github+json"
        })
        self.base=f"https://api.github.com/repos/{CFG.github_owner}/{CFG.github_repo}"
        return self
    def __exit__(self,*_):
        self.session.close()
    def list_files(self):
        r=self.session.get(f"{self.base}/contents/{CFG.github_folder}?ref={CFG.github_branch}",timeout=30)
        r.raise_for_status()
        return [f for f in r.json() if f["type"]=="file" and f["name"].lower().endswith(".csv")]
    def download(self,url):
        r=self.session.get(url,timeout=60)
        r.raise_for_status()
        return pd.read_csv(StringIO(r.text))


class SnowflakeClient:
    def __enter__(self):
        self.conn=snowflake.connector.connect(
            account=CFG.account,user=CFG.user,password=CFG.password,
            warehouse=CFG.warehouse,database=CFG.database,
            schema=CFG.schema,role=CFG.role
        )
        self.execute("SELECT CURRENT_VERSION()")
        return self
    def __exit__(self,*_):
        self.conn.close()
    def execute(self,sql,params=None):
        with self.conn.cursor() as c:
            c.execute(sql,params)
    def file_exists(self,sha):
        with self.conn.cursor() as c:
            c.execute(f"SELECT COUNT(*) FROM {CFG.schema}.FILE_HISTORY WHERE FILE_SHA=%s AND SOURCE_SYSTEM=%s AND STATUS='SUCCESS'",(sha,SOURCE_SYSTEM))
            return c.fetchone()[0]>0
    def truncate(self):
        self.execute(f"TRUNCATE TABLE {CFG.schema}.{STG_TABLE}")
    def load(self,df):
        ok,_,rows,_=write_pandas(self.conn,df,STG_TABLE,database=CFG.database,schema=CFG.schema,auto_create_table=False)
        if not ok:
            raise PipelineError("write_pandas failed")
        return rows
    def merge(self):
        self.execute(SQLBuilder.merge(CFG.schema))


def run():
    batch_id=uuid.uuid4().hex
    metrics={"processed":0,"skipped":0,"rows":0}
    started=time.perf_counter()

    with GitHubClient() as gh, SnowflakeClient() as sf:
        sf.truncate()
        for file in gh.list_files():
            if sf.file_exists(file["sha"]):
                metrics["skipped"]+=1
                continue
            df=Transformer.transform(
                gh.download(file["download_url"]),
                file["name"],
                batch_id
            )
            metrics["rows"]+=sf.load(df)
            metrics["processed"]+=1

        try:
            sf.execute("BEGIN")
            sf.merge()
            sf.execute("COMMIT")
        except SnowflakeError:
            sf.execute("ROLLBACK")
            raise

    log_event(
        "Pipeline completed",
        batch=batch_id,
        processed=metrics["processed"],
        skipped=metrics["skipped"],
        rows=metrics["rows"],
        duration=f"{time.perf_counter()-started:.2f}s",
        host=socket.gethostname(),
        python=platform.python_version()
    )


if __name__ == "__main__":
    run()
