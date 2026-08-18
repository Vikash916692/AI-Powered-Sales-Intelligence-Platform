import os

os.chdir("..")
from pathlib import Path

import pandas as pd

from src.ingestion.database import get_engine

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# --------------------------------------------------
# Dataset configuration
# --------------------------------------------------

DATASETS = {
    "stg_customers": {
        "file": "olist_customers_dataset.csv",
    },

    "stg_products": {
        "file": "olist_products_dataset.csv",
    },

    "stg_sellers": {
        "file": "olist_sellers_dataset.csv",
    },

    "stg_orders": {
        "file": "olist_orders_dataset.csv",
    },

    "stg_order_items": {
        "file": "olist_order_items_dataset.csv",
    },

    "stg_payments": {
        "file": "olist_order_payments_dataset.csv",
    },

    "stg_reviews": {
        "file": "olist_order_reviews_dataset.csv",
    },

    "stg_geolocation": {
        "file": "olist_geolocation_dataset.csv",
    },

    "stg_category_translation": {
        "file": "product_category_name_translation.csv",
    },
}


# --------------------------------------------------
# Load one CSV into MySQL
# --------------------------------------------------

def load_table(table_name, filename, engine):

    file_path = RAW_DATA_DIR / filename

    print("\n" + "=" * 60)
    print(f"Loading: {filename}")
    print(f"Target:  {table_name}")
    print("=" * 60)

    # Check that file exists
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    # Read CSV
    df = pd.read_csv(file_path)

    print(f"Rows read: {len(df):,}")
    print(f"Columns:   {len(df.columns)}")

    # --------------------------------------------------
    # Convert date columns
    # --------------------------------------------------

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "shipping_limit_date",
        "review_creation_date",
        "review_answer_timestamp",
    ]

    for column in date_columns:

        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------
    # Replace NaN with None
    # --------------------------------------------------

    df = df.where(
        pd.notnull(df),
        None
    )

    # --------------------------------------------------
    # Load into MySQL
    # --------------------------------------------------

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi"
    )

    print(
        f"✓ Loaded {len(df):,} rows into {table_name}"
    )


# --------------------------------------------------
# Main ETL ingestion
# --------------------------------------------------

def main():

    print("\n")
    print("=" * 60)
    print("OLIST STAGING INGESTION")
    print("=" * 60)

    engine = get_engine()

    print("\n✓ MySQL connection established")

    # IMPORTANT:
    # Parent tables must be loaded before child tables
    load_order = [
        "stg_customers",
        "stg_products",
        "stg_sellers",
        "stg_orders",
        "stg_order_items",
        "stg_payments",
        "stg_reviews",
        "stg_geolocation",
        "stg_category_translation",
    ]

    for table_name in load_order:

        config = DATASETS[table_name]

        load_table(
            table_name=table_name,
            filename=config["file"],
            engine=engine
        )

    print("\n")
    print("=" * 60)
    print("INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()