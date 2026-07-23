import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_CONNECTION_STRING")

if not DATABASE_URL:
    raise ValueError(
        "POSTGRES_CONNECTION_STRING not found in .env file"
    )

# =========================================================
# CONFIGURATION
# =========================================================

SCHEMA = "b2b_ticketing"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "generated_data"

# =========================================================
# DATABASE CONNECTION
# =========================================================

print("Connecting to Neon PostgreSQL...")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

with engine.connect() as conn:
    db_name = conn.execute(
        text("SELECT current_database();")
    ).scalar()

    print(f"Connected to database: {db_name}")

# =========================================================
# LOAD CSV FILES
# =========================================================

print("\nLoading CSV files...")

organizers_df = pd.read_csv(DATA_DIR / "organizers.csv")
resellers_df = pd.read_csv(DATA_DIR / "resellers.csv")
commission_df = pd.read_csv(DATA_DIR / "commission_agreements.csv")
events_df = pd.read_csv(DATA_DIR / "events.csv")
customers_df = pd.read_csv(DATA_DIR / "customers.csv")
sales_df = pd.read_csv(DATA_DIR / "ticket_sales.csv")

print("CSV files loaded successfully.")

# =========================================================
# DATE CONVERSIONS
# =========================================================

if "event_date" in events_df.columns:
    events_df["event_date"] = pd.to_datetime(
        events_df["event_date"]
    ).dt.date

if "purchase_date" in sales_df.columns:
    sales_df["purchase_date"] = pd.to_datetime(
        sales_df["purchase_date"]
    ).dt.date

if "effective_from" in commission_df.columns:
    commission_df["effective_from"] = pd.to_datetime(
        commission_df["effective_from"]
    ).dt.date

if "effective_to" in commission_df.columns:
    commission_df["effective_to"] = pd.to_datetime(
        commission_df["effective_to"]
    ).dt.date

# =========================================================
# TRUNCATE EXISTING DATA
# =========================================================

print("\nRemoving existing source data...")

with engine.begin() as conn:

    conn.execute(text(f"""
        TRUNCATE TABLE
            {SCHEMA}.ticket_sales,
            {SCHEMA}.events,
            {SCHEMA}.commission_agreements,
            {SCHEMA}.customers,
            {SCHEMA}.resellers,
            {SCHEMA}.organizers
        RESTART IDENTITY CASCADE;
    """))

print("Existing data removed.")

# =========================================================
# LOAD TABLES IN FK ORDER
# =========================================================

print("\nLoading organizers...")

organizers_df.to_sql(
    "organizers",
    engine,
    schema=SCHEMA,
    if_exists="append",
    index=False,
    chunksize=5000,
    method="multi"
)

print("Loading resellers...")

resellers_df.to_sql(
    "resellers",
    engine,
    schema=SCHEMA,
    if_exists="append",
    index=False,
    chunksize=5000,
    method="multi"
)

print("Loading commission agreements...")

commission_df.to_sql(
    "commission_agreements",
    engine,
    schema=SCHEMA,
    if_exists="append",
    index=False,
    chunksize=5000,
    method="multi"
)

print("Loading events...")

events_df.to_sql(
    "events",
    engine,
    schema=SCHEMA,
    if_exists="append",
    index=False,
    chunksize=5000,
    method="multi"
)

print("Loading customers...")

customers_df.to_sql(
    "customers",
    engine,
    schema=SCHEMA,
    if_exists="append",
    index=False,
    chunksize=5000,
    method="multi"
)

print("Loading ticket sales...")

sales_df.to_sql(
    "ticket_sales",
    engine,
    schema=SCHEMA,
    if_exists="append",
    index=False,
    chunksize=10000,
    method="multi"
)

# =========================================================
# VERIFY LOAD
# =========================================================

print("\nVerifying row counts...")

queries = {
    "organizers":
        f"SELECT COUNT(*) FROM {SCHEMA}.organizers",

    "resellers":
        f"SELECT COUNT(*) FROM {SCHEMA}.resellers",

    "commission_agreements":
        f"SELECT COUNT(*) FROM {SCHEMA}.commission_agreements",

    "events":
        f"SELECT COUNT(*) FROM {SCHEMA}.events",

    "customers":
        f"SELECT COUNT(*) FROM {SCHEMA}.customers",

    "ticket_sales":
        f"SELECT COUNT(*) FROM {SCHEMA}.ticket_sales"
}

with engine.connect() as conn:

    for table_name, sql in queries.items():

        count = conn.execute(
            text(sql)
        ).scalar()

        print(
            f"{table_name:<25}: {count:,}"
        )

# =========================================================
# SUMMARY
# =========================================================

print("\n===================================")
print("SOURCE DATA LOAD COMPLETED")
print("===================================")

print(f"Organizers            : {len(organizers_df):,}")
print(f"Resellers             : {len(resellers_df):,}")
print(f"Commission Agreements : {len(commission_df):,}")
print(f"Events                : {len(events_df):,}")
print(f"Customers             : {len(customers_df):,}")
print(f"Ticket Sales          : {len(sales_df):,}")

print("\nData successfully loaded into Neon.")

