import os
import uuid

from pathlib import Path

from datetime import datetime, timezone


import pandas as pd

from sqlalchemy import create_engine, text

import snowflake.connector

from dotenv import load_dotenv



# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()



# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


TEMP_DIR = BASE_DIR / "temp"


MERGE_SQL_FILE = (
    BASE_DIR
    / "sql"
    / "snowflake"
    / "merge_raw_tables.sql"
)


TEMP_DIR.mkdir(
    exist_ok=True
)



# ============================================================
# BATCH INFORMATION
# ============================================================

BATCH_ID = str(
    uuid.uuid4()
)


JOB_START_TIME = datetime.now(
    timezone.utc
)



# ============================================================
# TABLE CONFIGURATION
# ============================================================

TABLES = {


    "ORGANIZERS":
    {

        "source":
        "b2b_ticketing.organizers",

        "staging":
        "RAW.STG_ORGANIZERS",

        "target":
        "RAW.ORGANIZERS",

        "stage":
        "NEON/ORGANIZERS"

    },


    "RESELLERS":
    {

        "source":
        "b2b_ticketing.resellers",

        "staging":
        "RAW.STG_RESELLERS",

        "target":
        "RAW.RESELLERS",

        "stage":
        "NEON/RESELLERS"

    },


    "CUSTOMERS":
    {

        "source":
        "b2b_ticketing.customers",

        "staging":
        "RAW.STG_CUSTOMERS",

        "target":
        "RAW.CUSTOMERS",

        "stage":
        "NEON/CUSTOMERS"

    },


    "EVENTS":
    {

        "source":
        "b2b_ticketing.events",

        "staging":
        "RAW.STG_EVENTS",

        "target":
        "RAW.EVENTS",

        "stage":
        "NEON/EVENTS"

    },


    "COMMISSION_AGREEMENTS":
    {

        "source":
        "b2b_ticketing.commission_agreements",

        "staging":
        "RAW.STG_COMMISSION_AGREEMENTS",

        "target":
        "RAW.COMMISSION_AGREEMENTS",

        "stage":
        "NEON/COMMISSION_AGREEMENTS"

    },


    "TICKET_SALES":
    {

        "source":
        "b2b_ticketing.ticket_sales",

        "staging":
        "RAW.STG_TICKET_SALES",

        "target":
        "RAW.TICKET_SALES",

        "stage":
        "NEON/TICKET_SALES"

    }

}



# ============================================================
# NEON CONNECTION
# ============================================================
def get_neon_connection():

    connection_string = os.getenv(
        "POSTGRES_CONNECTION_STRING"
    )

    if not connection_string:
        raise ValueError(
            "POSTGRES_CONNECTION_STRING is not set."
        )

    print(f"Using Neon URL: {connection_string}")

    engine = create_engine(
        connection_string,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
        connect_args={
            "connect_timeout": 30
        }
    )

    return engine

# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

def get_snowflake_connection():


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
        WHERE SOURCE_TABLE = %s
        """,
        (
            table,
        )
    )

    result = cursor.fetchone()

    cursor.close()


    if result and result[0]:

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
            LAST_UPDATED_AT = %s,

            UPDATED_TS =
            CURRENT_TIMESTAMP()

        WHERE SOURCE_TABLE = %s
        """,

        (

            value,

            table

        )

    )


    cursor.close()




# ============================================================
# EXTRACT FROM NEON
# ============================================================

def extract(

    pg_engine,

    table,

    watermark

):


    source_table = TABLES[table]["source"]


    query = f"""

        SELECT *

        FROM {source_table}

        WHERE updated_at >
        '{watermark}'

        ORDER BY updated_at

    """


    print(f"Connecting to Neon for {table}")
    with pg_engine.connect() as conn:
        df = pd.read_sql(
            text(query),
            conn
        )

    print(
        f"{table} ROWS: {len(df)}"
    )


    return df





# ============================================================
# CLEAN TIMESTAMP COLUMNS
# ============================================================

def normalize_dataframe(

    df

):


    timestamp_columns = [

        "LOAD_TS",

        "UPDATED_AT"

    ]



    for col in timestamp_columns:


        if col in df.columns:


            df[col] = pd.to_datetime(

                df[col],

                errors="coerce"

            )



    return df





# ============================================================
# CREATE PARQUET
# ============================================================

def create_parquet(

    df,

    table

):


    df = normalize_dataframe(

        df

    )


    df["BATCH_ID"] = BATCH_ID


    df["SOURCE_SYSTEM"] = "NEON"



    df["LOAD_TS"] = datetime.now(

        timezone.utc

    )



    filename = (

        f"{table}_{BATCH_ID}.parquet"

    )



    filepath = (

        TEMP_DIR

        /

        filename

    )



    df.to_parquet(

        filepath,

        index=False

    )


    return filepath





# ============================================================
# CLEAR STAGE FOLDER
# ============================================================

def clear_stage_folder(

    sf,

    table

):


    cursor = sf.cursor()


    stage_path = (

        TABLES[table]["stage"]

    )


    cursor.execute(

        f"""

        REMOVE

        @RAW.INGEST_STAGE/{stage_path}/

        """

    )


    cursor.close()





# ============================================================
# PUT PARQUET TO SNOWFLAKE STAGE
# ============================================================

def put_file(

    sf,

    filepath,

    table

):


    cursor = sf.cursor()


    stage_path = (

        TABLES[table]["stage"]

    )


    cursor.execute(

        f"""

        PUT

        file://{filepath}

        @RAW.INGEST_STAGE/{stage_path}/


        AUTO_COMPRESS = TRUE


        OVERWRITE = TRUE


        """

    )


    cursor.close()





# ============================================================
# TRUNCATE STAGING TABLE
# ============================================================

def truncate_staging(

    sf,

    table

):


    cursor = sf.cursor()


    staging = TABLES[table]["staging"]


    cursor.execute(

        f"""

        TRUNCATE TABLE

        {staging}

        """

    )


    cursor.close()





# ============================================================
# COPY STAGE TO STAGING TABLE
# ============================================================

def copy_to_staging(

    sf,

    table

):


    cursor = sf.cursor()


    staging = TABLES[table]["staging"]


    stage_path = TABLES[table]["stage"]



    cursor.execute(

        f"""

        COPY INTO {staging}


        FROM

        @RAW.INGEST_STAGE/{stage_path}/



        FILE_FORMAT =

        (

            FORMAT_NAME =
            'RAW.PARQUET_FORMAT'

        )



        MATCH_BY_COLUMN_NAME =
        CASE_INSENSITIVE



        """

    )


    cursor.close()


    print(

        f"{table} COPIED TO STG"

    )
# ============================================================
# EXECUTE MERGE SQL
# ============================================================

def execute_merge(

    sf

):


    cursor = sf.cursor()


    with open(

        MERGE_SQL_FILE,

        "r"

    ) as file:


        sql = file.read()



    statements = [

        stmt.strip()

        for stmt in sql.split(";")

        if stmt.strip()

    ]



    for stmt in statements:


        cursor.execute(

            stmt

        )



    cursor.close()



    print(

        "MERGE COMPLETED"

    )





# ============================================================
# AUDIT
# ============================================================

def write_audit(

    sf,

    records

):


    cursor = sf.cursor()



    cursor.execute(

        """

        INSERT INTO AUDIT.JOB_AUDIT

        (

            JOB_NAME,

            START_TIME,

            END_TIME,

            STATUS,

            RECORDS_LOADED

        )


        VALUES

        (

            %s,

            %s,

            CURRENT_TIMESTAMP(),

            %s,

            %s

        )

        """,

        (

            "NEON_TO_SNOWFLAKE",

            JOB_START_TIME,

            "SUCCESS",

            records

        )

    )



    cursor.close()





# ============================================================
# MAIN LOAD PROCESS
# ============================================================

def main():


    pg = None

    sf = None


    total_records = 0


    watermark_updates = {}



    try:


        print("Creating Neon connection...")
        print("POSTGRES_CONNECTION_STRING:", os.getenv("POSTGRES_CONNECTION_STRING")
)
        pg = get_neon_connection()


        sf = get_snowflake_connection()



        for table in TABLES:


            print(

                f"PROCESSING {table}"

            )



            # --------------------------------
            # Get watermark
            # --------------------------------

            watermark = get_watermark(

                sf,

                table

            )



            # --------------------------------
            # Extract
            # --------------------------------

            df = extract(

                pg,

                table,

                watermark

            )



            if df.empty:


                print(

                    f"NO DATA {table}"

                )


                continue




            total_records += len(df)



            # --------------------------------
            # Save watermark
            # --------------------------------

            if "updated_at" in df.columns:


                watermark_updates[table] = (

                    pd.to_datetime(

                        df["updated_at"]

                    )

                    .max()

                    .to_pydatetime()

                )



            # --------------------------------
            # Clear stage
            # --------------------------------

            clear_stage_folder(

                sf,

                table

            )



            # --------------------------------
            # Truncate STG
            # --------------------------------

            truncate_staging(

                sf,

                table

            )



            # --------------------------------
            # Create parquet
            # --------------------------------

            parquet_file = create_parquet(

                df,

                table

            )



            # --------------------------------
            # PUT
            # --------------------------------

            put_file(

                sf,

                parquet_file,

                table

            )



            # --------------------------------
            # COPY
            # --------------------------------

            copy_to_staging(

                sf,

                table

            )




        # ------------------------------------
        # MERGE STG -> RAW
        # ------------------------------------

        execute_merge(

            sf

        )




        # ------------------------------------
        # Update watermark
        # ------------------------------------

        for table, value in watermark_updates.items():


            update_watermark(

                sf,

                table,

                value

            )





        # ------------------------------------
        # Audit
        # ------------------------------------

        write_audit(

            sf,

            total_records

        )



        print(

            "LOAD FINISHED"

        )


        print(

            f"TOTAL RECORDS: {total_records}"

        )



    finally:
        if pg:
            pg.dispose()
        if sf:
            sf.close()





# ============================================================
# LOCAL EXECUTION
# ============================================================

if __name__ == "__main__":


    main()