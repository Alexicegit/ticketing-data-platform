import os
import uuid

from pathlib import Path
from datetime import datetime

import pandas as pd

from sqlalchemy import create_engine, text

import snowflake.connector

from dotenv import load_dotenv



# ============================================================
# ENV
# ============================================================

load_dotenv()



# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


TEMP_DIR = BASE_DIR / "temp"


MERGE_SQL_FILE = (
    BASE_DIR
    /
    "sql"
    /
    "snowflake"
    /
    "merge_raw_tables.sql"
)


TEMP_DIR.mkdir(
    exist_ok=True
)



# ============================================================
# BATCH
# ============================================================

BATCH_ID = str(uuid.uuid4())


JOB_START_TIME = datetime.utcnow().strftime(
    "%Y-%m-%d %H:%M:%S"
)



# ============================================================
# TABLES
# ============================================================

TABLES = {

"ORGANIZERS":
{
"source":"b2b_ticketing.organizers",
"stage":"ORGANIZERS",
"stg":"RAW.STG_ORGANIZERS"
},


"RESELLERS":
{
"source":"b2b_ticketing.resellers",
"stage":"RESELLERS",
"stg":"RAW.STG_RESELLERS"
},


"CUSTOMERS":
{
"source":"b2b_ticketing.customers",
"stage":"CUSTOMERS",
"stg":"RAW.STG_CUSTOMERS"
},


"EVENTS":
{
"source":"b2b_ticketing.events",
"stage":"EVENTS",
"stg":"RAW.STG_EVENTS"
},


"COMMISSION_AGREEMENTS":
{
"source":"b2b_ticketing.commission_agreements",
"stage":"COMMISSION_AGREEMENTS",
"stg":"RAW.STG_COMMISSION_AGREEMENTS"
},


"TICKET_SALES":
{
"source":"b2b_ticketing.ticket_sales",
"stage":"TICKET_SALES",
"stg":"RAW.STG_TICKET_SALES"
}

}



# ============================================================
# CONNECTIONS
# ============================================================

def neon_connection():


    url = (

        "postgresql+psycopg2://"

        f"{os.getenv('NEON_USER')}:"

        f"{os.getenv('NEON_PASSWORD')}@"

        f"{os.getenv('NEON_HOST')}:"

        f"{os.getenv('NEON_PORT')}/"

        f"{os.getenv('NEON_DATABASE')}"

        "?sslmode=require"

    )


    return create_engine(
        url
    )





def snowflake_connection():


    return snowflake.connector.connect(

        account=os.getenv(
            "SNOWFLAKE_ACCOUNT"
        ),

        user=os.getenv(
            "SNOWFLAKE_USER"
        ),

        password=os.getenv(
            "SNOWFLAKE_PASSWORD"
        ),

        warehouse=os.getenv(
            "SNOWFLAKE_WAREHOUSE"
        ),

        database="B2B_EVENT_TICKETING",

        schema="RAW"

    )



# ============================================================
# CLEAN STAGE
# ============================================================

def clean_stage(sf):

    cursor = sf.cursor()


    cursor.execute(
        """
        REMOVE @RAW.INGEST_STAGE/NEON/
        """
    )


    cursor.close()



# ============================================================
# CLEAN STAGING
# ============================================================

def truncate_stg(sf):

    cursor = sf.cursor()


    for table in TABLES:


        cursor.execute(

            f"""
            TRUNCATE TABLE
            {TABLES[table]["stg"]}
            """

        )


    cursor.close()



# ============================================================
# WATERMARK
# ============================================================

def get_watermark(
        sf,
        table
):

    cursor = sf.cursor()


    cursor.execute(

        """

        SELECT LAST_UPDATED_AT

        FROM AUDIT.ETL_WATERMARK

        WHERE SOURCE_TABLE=%s

        """,

        (
            table,
        )

    )


    result = cursor.fetchone()


    cursor.close()


    if result:

        return result[0]


    return datetime(
        1900,
        1,
        1
    )





def update_watermark(
        sf,
        table,
        value
):

    cursor = sf.cursor()


    cursor.execute(

        """

        UPDATE AUDIT.ETL_WATERMARK

        SET

        LAST_UPDATED_AT =
        TO_TIMESTAMP_NTZ(%s),

        UPDATED_TS =
        CURRENT_TIMESTAMP()

        WHERE SOURCE_TABLE=%s

        """,

        (

        value.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        table

        )

    )


    cursor.close()



# ============================================================
# EXTRACT
# ============================================================

def extract(
        engine,
        table,
        watermark
):


    source = TABLES[table]["source"]


    sql = text(

        f"""

        SELECT *

        FROM {source}

        WHERE updated_at > :wm

        ORDER BY updated_at

        """

    )


    df = pd.read_sql(

        sql,

        engine,

        params={
            "wm": watermark
        }

    )


    print(
        table,
        "ROWS:",
        len(df)
    )


    return df



# ============================================================
# PARQUET
# ============================================================

def create_parquet(
        df,
        table
):


    # Convert timestamps to strings

    for col in df.columns:


        if (
            "date" in col.lower()
            or
            "time" in col.lower()
        ):


            df[col] = (

                pd.to_datetime(
                    df[col],
                    errors="coerce"
                )

                .dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            )



    df["BATCH_ID"] = BATCH_ID


    df["LOAD_TS"] = (
        datetime.utcnow()
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


    df["SOURCE_SYSTEM"] = "NEON"



    file = (

        TEMP_DIR

        /

        f"{table}_{BATCH_ID}.parquet"

    )


    df.to_parquet(
        file,
        index=False
    )


    return file



# ============================================================
# PUT
# ============================================================

def put_file(
        sf,
        file,
        table
):

    cursor = sf.cursor()


    cursor.execute(

        f"""

        PUT file://{file}

        @RAW.INGEST_STAGE/NEON/{table}/

        AUTO_COMPRESS=TRUE

        OVERWRITE=TRUE

        """

    )


    cursor.close()



# ============================================================
# COPY
# ============================================================

def copy_stg(
        sf,
        table
):


    cursor = sf.cursor()


    cursor.execute(

        f"""

        COPY INTO
        {TABLES[table]["stg"]}

        FROM
        @RAW.INGEST_STAGE/NEON/{table}/


        FILE_FORMAT=
        (
            FORMAT_NAME='RAW.PARQUET_FORMAT'
        )


        MATCH_BY_COLUMN_NAME =
        CASE_INSENSITIVE


        PURGE=FALSE

        """

    )


    cursor.close()



# ============================================================
# MERGE
# ============================================================

def merge(sf):


    cursor = sf.cursor()


    with open(
        MERGE_SQL_FILE
    ) as f:

        sql=f.read()



    for statement in sql.split(";"):


        if statement.strip():


            cursor.execute(
                statement
            )

            print(
                "MERGE DONE"
            )


    cursor.close()



# ============================================================
# MAIN
# ============================================================

def main():


    neon = neon_connection()


    sf = snowflake_connection()


    watermark_updates={}


    total=0



    try:


        clean_stage(sf)


        truncate_stg(sf)



        for table in TABLES:


            wm=get_watermark(
                sf,
                table
            )


            df=extract(
                neon,
                table,
                wm
            )



            if df.empty:

                continue



            total += len(df)



            max_updated = pd.to_datetime(
                df["updated_at"]
            ).max()



            watermark_updates[table]=datetime.strptime(

                str(max_updated)[:19],

                "%Y-%m-%d %H:%M:%S"

            )



            file=create_parquet(
                df,
                table
            )


            put_file(
                sf,
                file,
                table
            )


            copy_stg(
                sf,
                table
            )



        merge(sf)



        for table,value in watermark_updates.items():


            update_watermark(
                sf,
                table,
                value
            )


        print(
            "TOTAL RECORDS:",
            total
        )


    finally:


        neon.dispose()

        sf.close()



if __name__=="__main__":

    main()