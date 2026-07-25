from pathlib import Path
import pandas as pd
import random

# =========================================================
# CONFIG
# =========================================================

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "generated_data"

RESELLER_DIR = DATA_DIR / "reseller_files"

RESELLER_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# LOAD GENERATED SOURCE DATA
# =========================================================

print("Loading source data...")

events_df = pd.read_csv(DATA_DIR / "events.csv")
customers_df = pd.read_csv(DATA_DIR / "customers.csv")
resellers_df = pd.read_csv(DATA_DIR / "resellers.csv")
sales_df = pd.read_csv(DATA_DIR / "ticket_sales.csv")

# =========================================================
# RESELLERS USING CSV INTEGRATION
# =========================================================

csv_resellers = [
    "RES001",
    "RES005",
    "RES010"
]

# =========================================================
# FILES TO GENERATE
# =========================================================

files_to_generate = [
    ("01012020", "RES001"),
    ("01052020", "RES005"),
    ("01102020", "RES010"),
    ("02012020", "RES001"),
    ("02152020", "RES005"),
    ("03012020", "RES010"),
    ("04012020", "RES001"),
    ("05012020", "RES005"),
    ("06012020", "RES010"),
    ("07012020", "RES001"),
    ("08012020", "RES005"),
    ("09012020", "RES010")
]

# =========================================================
# LOOKUPS
# =========================================================

events_lookup = (
    events_df[
        ["event_id", "event_name"]
    ]
    .set_index("event_id")
    .to_dict()["event_name"]
)

customers_lookup = (
    customers_df[
        ["customer_id", "first_name", "last_name"]
    ]
    .set_index("customer_id")
    .to_dict("index")
)

office_locations = {
    "RES001": "California Office",
    "RES005": "Texas Office",
    "RES010": "New York Office"
}

sales_channel_mapping = {
    "WEB": "web",
    "MOBILE_APP": "mobile_app",
    "ON_SITE": "on_site"
}

# =========================================================
# GENERATE FILES
# =========================================================

print("Generating reseller CSV files...")

transaction_id = 100000000

for file_date, reseller_id in files_to_generate:

    reseller_sales = sales_df[
        sales_df["reseller_id"] == reseller_id
    ]

    sample_sales = reseller_sales.sample(
        n=min(25, len(reseller_sales)),
        random_state=42
    )

    rows = []

    for _, sale in sample_sales.iterrows():

        transaction_id += 1

        customer = customers_lookup[
            sale["customer_id"]
        ]

        rows.append({
            "Transaction ID": transaction_id,
            "Event name": events_lookup[
                sale["event_id"]
            ],
            "Number of purchased tickets": int(
                sale["quantity"]
            ),
            "Total amount": float(
                sale["total_amount"]
            ),
            "Sales channel": sales_channel_mapping.get(
                sale["sales_channel"],
                "web"
            ),
            "Customer first name": customer[
                "first_name"
            ],
            "Customer last name": customer[
                "last_name"
            ],
            "Office location": office_locations[
                reseller_id
            ],
            "Created Date": pd.to_datetime(
                file_date,
                format="%m%d%Y"
            ).strftime("%Y-%m-%d")
        })

    output_file = (
        RESELLER_DIR
        / f"DailySales_{file_date}_{reseller_id}.csv"
    )

    pd.DataFrame(rows).to_csv(
        output_file,
        index=False
    )

    print(f"Created {output_file.name}")

print("\nReseller CSV generation complete.")
print(f"Files written to: {RESELLER_DIR}")