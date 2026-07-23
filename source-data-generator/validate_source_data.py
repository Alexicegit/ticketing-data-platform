from pathlib import Path
import pandas as pd

# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "generated_data"

# =========================================================
# LOAD FILES
# =========================================================

print("Loading source files...")

organizers_df = pd.read_csv(DATA_DIR / "organizers.csv")
resellers_df = pd.read_csv(DATA_DIR / "resellers.csv")
commission_df = pd.read_csv(DATA_DIR / "commission_agreements.csv")
events_df = pd.read_csv(DATA_DIR / "events.csv")
customers_df = pd.read_csv(DATA_DIR / "customers.csv")
sales_df = pd.read_csv(DATA_DIR / "ticket_sales.csv")

print("Files loaded successfully.\n")

# =========================================================
# VALIDATION RESULTS
# =========================================================

validation_errors = []

# =========================================================
# HELPER
# =========================================================

def validate(condition, success_msg, error_msg):
    if condition:
        print(f"[PASS] {success_msg}")
    else:
        print(f"[FAIL] {error_msg}")
        validation_errors.append(error_msg)

# =========================================================
# ROW COUNTS
# =========================================================

print("========================================")
print("ROW COUNT VALIDATION")
print("========================================")

validate(len(organizers_df) > 0,
         "Organizers loaded",
         "Organizers missing")

validate(len(resellers_df) > 0,
         "Resellers loaded",
         "Resellers missing")

validate(len(commission_df) > 0,
         "Commission agreements loaded",
         "Commission agreements missing")

validate(len(events_df) > 0,
         "Events loaded",
         "Events missing")

validate(len(customers_df) > 0,
         "Customers loaded",
         "Customers missing")

validate(len(sales_df) > 0,
         "Ticket sales loaded",
         "Ticket sales missing")

# =========================================================
# PRIMARY KEYS
# =========================================================

print("\n========================================")
print("PRIMARY KEY VALIDATION")
print("========================================")

validate(
    organizers_df["organizer_id"].is_unique,
    "Unique organizer_id",
    "Duplicate organizer_id detected"
)

validate(
    resellers_df["reseller_id"].is_unique,
    "Unique reseller_id",
    "Duplicate reseller_id detected"
)

validate(
    events_df["event_id"].is_unique,
    "Unique event_id",
    "Duplicate event_id detected"
)

validate(
    customers_df["customer_id"].is_unique,
    "Unique customer_id",
    "Duplicate customer_id detected"
)

validate(
    sales_df["ticket_id"].is_unique,
    "Unique ticket_id",
    "Duplicate ticket_id detected"
)

# =========================================================
# FOREIGN KEYS
# =========================================================

print("\n========================================")
print("FOREIGN KEY VALIDATION")
print("========================================")

invalid_event_orgs = events_df[
    ~events_df["organizer_id"].isin(
        organizers_df["organizer_id"]
    )
]

validate(
    len(invalid_event_orgs) == 0,
    "Events -> Organizers valid",
    f"{len(invalid_event_orgs)} invalid organizer references in events"
)

invalid_comm_orgs = commission_df[
    ~commission_df["organizer_id"].isin(
        organizers_df["organizer_id"]
    )
]

validate(
    len(invalid_comm_orgs) == 0,
    "Commission -> Organizers valid",
    f"{len(invalid_comm_orgs)} invalid organizer references in commission agreements"
)

invalid_comm_resellers = commission_df[
    ~commission_df["reseller_id"].isin(
        resellers_df["reseller_id"]
    )
]

validate(
    len(invalid_comm_resellers) == 0,
    "Commission -> Resellers valid",
    f"{len(invalid_comm_resellers)} invalid reseller references in commission agreements"
)

invalid_sales_events = sales_df[
    ~sales_df["event_id"].isin(
        events_df["event_id"]
    )
]

validate(
    len(invalid_sales_events) == 0,
    "Sales -> Events valid",
    f"{len(invalid_sales_events)} invalid event references in sales"
)

invalid_sales_customers = sales_df[
    ~sales_df["customer_id"].isin(
        customers_df["customer_id"]
    )
]

validate(
    len(invalid_sales_customers) == 0,
    "Sales -> Customers valid",
    f"{len(invalid_sales_customers)} invalid customer references in sales"
)

invalid_sales_resellers = sales_df[
    ~sales_df["reseller_id"].isin(
        resellers_df["reseller_id"]
    )
]

validate(
    len(invalid_sales_resellers) == 0,
    "Sales -> Resellers valid",
    f"{len(invalid_sales_resellers)} invalid reseller references in sales"
)

# =========================================================
# COMMISSION RELATIONSHIP VALIDATION
# =========================================================

print("\n========================================")
print("BUSINESS RULE VALIDATION")
print("========================================")

event_lookup = (
    events_df
    .set_index("event_id")
    .to_dict("index")
)

valid_pairs = set(
    zip(
        commission_df["organizer_id"],
        commission_df["reseller_id"]
    )
)

invalid_relationships = 0

for row in sales_df.itertuples():

    organizer_id = event_lookup[row.event_id]["organizer_id"]

    if (organizer_id, row.reseller_id) not in valid_pairs:
        invalid_relationships += 1

validate(
    invalid_relationships == 0,
    "Sales reseller matches organizer commission agreement",
    f"{invalid_relationships} invalid organizer/reseller combinations"
)

# =========================================================
# DATE VALIDATION
# =========================================================

print("\n========================================")
print("DATE VALIDATION")
print("========================================")

events_df["event_date"] = pd.to_datetime(events_df["event_date"])
sales_df["purchase_date"] = pd.to_datetime(sales_df["purchase_date"])

validate(
    events_df["event_date"].min() >= pd.Timestamp("2019-01-01"),
    "Event dates start within expected range",
    "Event dates before 2019-01-01 detected"
)

validate(
    events_df["event_date"].max() <= pd.Timestamp("2020-12-31"),
    "Event dates end within expected range",
    "Event dates after 2020-12-31 detected"
)

validate(
    sales_df["purchase_date"].min() >= pd.Timestamp("2019-01-01"),
    "Purchase dates start within expected range",
    "Purchase dates before 2019-01-01 detected"
)

validate(
    sales_df["purchase_date"].max() <= pd.Timestamp("2020-12-31"),
    "Purchase dates end within expected range",
    "Purchase dates after 2020-12-31 detected"
)

# =========================================================
# DATA QUALITY CHECKS
# =========================================================

print("\n========================================")
print("DATA QUALITY CHECKS")
print("========================================")

negative_qty = len(
    sales_df[sales_df["quantity"] <= 0]
)

negative_price = len(
    sales_df[sales_df["unit_price"] <= 0]
)

invalid_channels = len(
    sales_df[
        ~sales_df["sales_channel"].isin(
            ["WEB", "MOBILE_APP", "ON_SITE"]
        )
    ]
)

amount_mismatch = len(
    sales_df[
        (
            sales_df["quantity"]
            * sales_df["unit_price"]
        ).round(2)
        != sales_df["total_amount"].round(2)
    ]
)

print(f"Negative Quantity Records : {negative_qty}")
print(f"Negative Price Records    : {negative_price}")
print(f"Invalid Channels          : {invalid_channels}")
print(f"Amount Mismatches         : {amount_mismatch}")

# =========================================================
# YEAR COMPARISON
# =========================================================

print("\n========================================")
print("SALES BY YEAR")
print("========================================")

sales_by_year = (
    sales_df
    .groupby(
        sales_df["purchase_date"].dt.year
    )["total_amount"]
    .sum()
)

print(sales_by_year)

# =========================================================
# SUMMARY
# =========================================================

print("\n========================================")
print("VALIDATION SUMMARY")
print("========================================")

if len(validation_errors) == 0:
    print("ALL STRUCTURAL VALIDATIONS PASSED")
else:
    print(f"{len(validation_errors)} VALIDATION ERRORS FOUND")

    for err in validation_errors:
        print(f" - {err}")

