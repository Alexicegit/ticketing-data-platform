import os
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd
from faker import Faker
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

fake = Faker()
random.seed(42)
np.random.seed(42)



BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "generated_data"

OUTPUT_DIR.mkdir(exist_ok=True)

# =========================================================
# CLEAN OUTPUT FOLDER
# =========================================================
# Set True to delete old CSV files
# Set False to keep existing files
CLEAN_OUTPUT_FOLDER = True


def cleanup_output_folder(output_dir: Path):
    """
    Remove all existing CSV files from output folder.
    """

    if not output_dir.exists():
        return

    for file in output_dir.glob("*.csv"):
        file.unlink()
        print(f"Deleted {file.name}")


if CLEAN_OUTPUT_FOLDER:
    print("Cleaning output directory...")
    cleanup_output_folder(OUTPUT_DIR)



NUM_ORGANIZERS = 20
NUM_RESELLERS = 50
NUM_CUSTOMERS = 20000
NUM_EVENTS = 1000
NUM_SALES = 100000

START_DATE = date(2019, 1, 1)
END_DATE = date(2020, 12, 31)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================================================
# MASTER DATA
# =========================================================

REGIONS = [
    "California",
    "Texas",
    "Florida",
    "New York",
    "Illinois"
]

COUNTRIES = [
    "USA",
    "Canada",
    "UK",
    "Germany",
    "France"
]

EVENT_TYPES_BY_REGION = {
    "California": ["Music", "Music", "Festival", "Music"],
    "Texas": ["Sports", "Sports", "Business"],
    "Florida": ["Festival", "Music", "Sports"],
    "New York": ["Business", "Business", "Theater"],
    "Illinois": ["Music", "Sports", "Business"]
}

SALES_CHANNELS = [
    "WEB",
    "MOBILE_APP",
    "ON_SITE"
]

# =========================================================
# HELPERS
# =========================================================

def random_date(start_date, end_date):
    delta = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, delta))

def weighted_purchase_date():
    year = random.choices(
        [2019, 2020],
        weights=[40, 60]
    )[0]

    month_weights = [
        0.8, 1.0, 1.0, 1.1, 1.2, 1.3,
        1.4, 1.4, 1.2, 1.1, 1.5, 1.8
    ]

    month = random.choices(
        range(1, 13),
        weights=month_weights
    )[0]

    day = random.randint(1, 28)

    return date(year, month, day)

# =========================================================
# ORGANIZERS
# =========================================================

print("Generating organizers...")

organizers = []

for i in range(1, NUM_ORGANIZERS + 1):

    organizers.append({
        "organizer_id": f"ORG{i:03}",
        "organizer_name": fake.company(),
        "country": random.choice(COUNTRIES),
        "region": random.choice(REGIONS)
    })

organizers_df = pd.DataFrame(organizers)

# =========================================================
# RESELLERS
# =========================================================

print("Generating resellers...")

resellers = []

for i in range(1, NUM_RESELLERS + 1):

    resellers.append({
        "reseller_id": f"RES{i:03}",
        "reseller_name": fake.company(),
        "country": random.choice(COUNTRIES),
        "region": random.choice(REGIONS)
    })

resellers_df = pd.DataFrame(resellers)

# =========================================================
# COMMISSION AGREEMENTS
# =========================================================

print("Generating commission agreements...")

agreements = []

agreement_id = 1

for organizer_id in organizers_df["organizer_id"]:

    selected_resellers = random.sample(
        list(resellers_df["reseller_id"]),
        10
    )

    for reseller_id in selected_resellers:

        agreements.append({
            "agreement_id": agreement_id,
            "organizer_id": organizer_id,
            "reseller_id": reseller_id,
            "commission_rate": round(
                random.uniform(5, 20),
                2
            ),
            "effective_from": START_DATE,
            "effective_to": END_DATE
        })

        agreement_id += 1

commission_df = pd.DataFrame(agreements)


# =========================================================
# EVENTS
# =========================================================

print("Generating events...")

events = []

used_event_names = set()


EVENT_PREFIXES = [
    "Global",
    "Annual",
    "International",
    "Premier",
    "Ultimate",
    "National",
    "World",
    "City",
    "Elite",
    "Grand"
]


EVENT_NAMES = [
    "Championship",
    "Festival",
    "Conference",
    "Summit",
    "Concert",
    "Showcase",
    "Expo",
    "Tournament",
    "Awards",
    "Experience"
]


for i in range(1, NUM_EVENTS + 1):

    organizer = organizers_df.sample(1).iloc[0]

    region = organizer["region"]

    event_type = random.choice(
        EVENT_TYPES_BY_REGION[region]
    )


    event_date = random_date(
        START_DATE,
        END_DATE
    )


    # Generate unique event name

    while True:

        event_name = (
            f"{random.choice(EVENT_PREFIXES)} "
            f"{random.choice(EVENT_NAMES)} "
            f"{fake.city()} "
            f"{event_date.year}"
        )


        if event_name not in used_event_names:
            used_event_names.add(event_name)
            break


    events.append({

        "event_id":
            f"EVT{i:05}",

        "organizer_id":
            organizer["organizer_id"],

        "event_name":
            event_name,

        "event_type":
            event_type,

        "venue":
            fake.company(),

        "region":
            region,

        "event_date":
            event_date

    })


events_df = pd.DataFrame(events)

# =========================================================
# CUSTOMERS
# =========================================================

print("Generating customers...")

customers = []

for i in range(1, NUM_CUSTOMERS + 1):

    customers.append({
        "customer_id": f"CUST{i:06}",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
        "country": random.choice(COUNTRIES)
    })

customers_df = pd.DataFrame(customers)

# =========================================================
# LOOKUPS
# =========================================================

event_lookup = (
    events_df
    .set_index("event_id")
    .to_dict("index")
)

commission_lookup = {}

for _, row in commission_df.iterrows():

    commission_lookup.setdefault(
        row["organizer_id"],
        []
    ).append(
        row["reseller_id"]
    )

event_ids = events_df["event_id"].tolist()
customer_ids = customers_df["customer_id"].tolist()

# =========================================================
# LOOKUPS
# =========================================================

event_lookup = (
    events_df
    .set_index("event_id")
    .to_dict("index")
)

commission_lookup = {}

for _, row in commission_df.iterrows():

    commission_lookup.setdefault(
        row["organizer_id"],
        []
    ).append(
        row["reseller_id"]
    )

event_ids = events_df["event_id"].tolist()
customer_ids = customers_df["customer_id"].tolist()


# =========================================================
# ADD THESE LOOKUPS
# =========================================================

organizer_lookup = (
    organizers_df
    .set_index("organizer_id")
    .to_dict("index")
)

reseller_lookup = (
    resellers_df
    .set_index("reseller_id")
    .to_dict("index")
)

# =========================================================
# TICKET SALES
# =========================================================

# =========================================================
# TICKET SALES
# =========================================================

print("Generating ticket sales...")

sales = []

SELLER_TYPE_WEIGHTS = [30, 70]
SALES_CHANNEL_WEIGHTS = [55, 30, 15]
QUANTITY_WEIGHTS = [45, 25, 15, 8, 5, 2]

EVENT_TYPE_PRICE = {
    "Music": (40, 180),
    "Sports": (50, 250),
    "Festival": (30, 140),
    "Business": (120, 350),
    "Theater": (60, 220)
}

for i in range(1, NUM_SALES + 1):

    event_id = random.choice(event_ids)

    event = event_lookup[event_id]

    organizer_id = event["organizer_id"]

    organizer_name = organizer_lookup[organizer_id]["organizer_name"]

    event_type = event["event_type"]

    # ----------------------------------------------------
    # Seller
    # ----------------------------------------------------

    seller_type = random.choices(
        ["ORGANIZER", "RESELLER"],
        weights=SELLER_TYPE_WEIGHTS
    )[0]

    if seller_type == "RESELLER":

        reseller_id = random.choice(
            commission_lookup[organizer_id]
        )

        seller_id = reseller_id

        seller_name = reseller_lookup[reseller_id]["reseller_name"]

    else:

        reseller_id = None

        seller_id = organizer_id

        seller_name = organizer_name

    # ----------------------------------------------------
    # Sales Channel
    # ----------------------------------------------------

    sales_channel = random.choices(
        SALES_CHANNELS,
        weights=SALES_CHANNEL_WEIGHTS
    )[0]

    # ----------------------------------------------------
    # Quantity
    # ----------------------------------------------------

    quantity = random.choices(
        [1, 2, 3, 4, 5, 6],
        weights=QUANTITY_WEIGHTS
    )[0]

    # ----------------------------------------------------
    # Ticket Price
    # ----------------------------------------------------

    min_price, max_price = EVENT_TYPE_PRICE[event_type]

    unit_price = round(
        random.uniform(
            min_price,
            max_price
        ),
        2
    )

    # ----------------------------------------------------
    # Promotional Discounts
    # ----------------------------------------------------

    if random.random() < 0.12:
        unit_price = round(unit_price * 0.85, 2)

    total_amount = round(
        quantity * unit_price,
        2
    )

    sales.append({

        "ticket_id": f"TKT{i:08}",

        "event_id": event_id,

        "organizer_id": organizer_id,

        "reseller_id": reseller_id,

        "seller_type": seller_type,

        "seller_id": seller_id,

        "seller_name": seller_name,

        "customer_id": random.choice(customer_ids),

        "sales_channel": sales_channel,

        "quantity": quantity,

        "unit_price": unit_price,

        "total_amount": total_amount,

        "purchase_date": weighted_purchase_date()

    })

    if i % 10000 == 0:
        print(f"{i:,} sales generated")

sales_df = pd.DataFrame(sales)

# =========================================================
# OPTIONAL BAD RECORDS FOR ETL TESTING
# =========================================================

GENERATE_BAD_DATA = False

if GENERATE_BAD_DATA:

    bad_rows = min(1000, len(sales_df))

    bad_indices = random.sample(
        list(sales_df.index),
        bad_rows
    )

    for idx in bad_indices[:300]:
        sales_df.loc[idx, "quantity"] = -1

    for idx in bad_indices[300:600]:
        sales_df.loc[idx, "unit_price"] = -100

    for idx in bad_indices[600:800]:
        sales_df.loc[idx, "sales_channel"] = "FACEBOOK"

    for idx in bad_indices[800:1000]:
        sales_df.loc[idx, "total_amount"] = 999999

# =========================================================
# EXPORT
# =========================================================

print("Writing CSV files...")

organizers_df.to_csv(
    f"{OUTPUT_DIR}/organizers.csv",
    index=False
)

resellers_df.to_csv(
    f"{OUTPUT_DIR}/resellers.csv",
    index=False
)

commission_df.to_csv(
    f"{OUTPUT_DIR}/commission_agreements.csv",
    index=False
)

events_df.to_csv(
    f"{OUTPUT_DIR}/events.csv",
    index=False
)

customers_df.to_csv(
    f"{OUTPUT_DIR}/customers.csv",
    index=False
)

sales_df.to_csv(
    f"{OUTPUT_DIR}/ticket_sales.csv",
    index=False
)

print("\nData generation complete.")
print(f"Files written to: {OUTPUT_DIR}")

print(len(organizers_df))
print(len(resellers_df))
print(len(commission_df))
print(len(events_df))
print(len(customers_df))
print(len(sales_df))