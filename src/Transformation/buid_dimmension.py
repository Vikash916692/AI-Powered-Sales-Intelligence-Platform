
import sys
from pathlib import Path

# Ensure project root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from sqlalchemy import text

from src.ingestion.database import get_engine


def build_dim_customer(engine):
    """
    Populate dim_customer from stg_customers.
    """

    print("\nBuilding dim_customer...")

    query = text("""
        INSERT INTO dim_customer (
            customer_id,
            customer_unique_id,
            customer_zip_code_prefix,
            customer_city,
            customer_state
        )
        SELECT
            customer_id,
            customer_unique_id,
            customer_zip_code_prefix,
            customer_city,
            customer_state
        FROM stg_customers
        ON DUPLICATE KEY UPDATE
            customer_unique_id = VALUES(customer_unique_id),
            customer_zip_code_prefix = VALUES(customer_zip_code_prefix),
            customer_city = VALUES(customer_city),
            customer_state = VALUES(customer_state);
    """)

    with engine.begin() as connection:
        connection.execute(query)

    print("[OK] dim_customer completed")


def build_dim_product(engine):
    """
    Populate dim_product from products and category translation.
    """

    print("\nBuilding dim_product...")

    query = text("""
        INSERT INTO dim_product (
            product_id,
            category_name,
            category_name_english,
            product_name_length,
            product_description_length,
            product_photos_qty,
            product_weight_g,
            product_length_cm,
            product_height_cm,
            product_width_cm
        )
        SELECT
            p.product_id,
            p.product_category_name,
            ct.product_category_name_english,
            p.product_name_lenght,
            p.product_description_lenght,
            p.product_photos_qty,
            p.product_weight_g,
            p.product_length_cm,
            p.product_height_cm,
            p.product_width_cm

        FROM stg_products p

        LEFT JOIN stg_category_translation ct
            ON p.product_category_name =
               ct.product_category_name

        ON DUPLICATE KEY UPDATE
            category_name = VALUES(category_name),
            category_name_english = VALUES(category_name_english),
            product_name_length = VALUES(product_name_length),
            product_description_length =
                VALUES(product_description_length),
            product_photos_qty = VALUES(product_photos_qty),
            product_weight_g = VALUES(product_weight_g),
            product_length_cm = VALUES(product_length_cm),
            product_height_cm = VALUES(product_height_cm),
            product_width_cm = VALUES(product_width_cm);
    """)

    with engine.begin() as connection:
        connection.execute(query)

    print("[OK] dim_product completed")


def build_dim_seller(engine):
    """
    Populate dim_seller from stg_sellers.
    """

    print("\nBuilding dim_seller...")

    query = text("""
        INSERT INTO dim_seller (
            seller_id,
            seller_zip_code_prefix,
            seller_city,
            seller_state
        )
        SELECT
            seller_id,
            seller_zip_code_prefix,
            seller_city,
            seller_state
        FROM stg_sellers

        ON DUPLICATE KEY UPDATE
            seller_zip_code_prefix =
                VALUES(seller_zip_code_prefix),
            seller_city = VALUES(seller_city),
            seller_state = VALUES(seller_state);
    """)

    with engine.begin() as connection:
        connection.execute(query)

    print("[OK] dim_seller completed")


def build_dim_geography(engine):
    """
    Create one representative geography record
    for each ZIP code prefix.
    """

    print("\nBuilding dim_geography...")

    query = text("""
        INSERT INTO dim_geography (
            zip_code_prefix,
            city,
            state,
            latitude,
            longitude
        )
        SELECT
            geolocation_zip_code_prefix,
            MIN(geolocation_city) AS city,
            MIN(geolocation_state) AS state,
            AVG(geolocation_lat) AS latitude,
            AVG(geolocation_lng) AS longitude

        FROM stg_geolocation

        GROUP BY geolocation_zip_code_prefix

        ON DUPLICATE KEY UPDATE
            city = VALUES(city),
            state = VALUES(state),
            latitude = VALUES(latitude),
            longitude = VALUES(longitude);
    """)

    with engine.begin() as connection:
        connection.execute(query)

    print("[OK] dim_geography completed")


def build_dim_date(engine):
    """
    Populate dim_date using all relevant dates
    found in the orders table.
    """

    print("\nBuilding dim_date...")

    query = text("""
        INSERT IGNORE INTO dim_date (
            date_key,
            full_date,
            year,
            quarter,
            month,
            month_name,
            week_of_year,
            day_of_month,
            day_of_week,
            day_name,
            is_weekend
        )

        SELECT DISTINCT

            DATE_FORMAT(
                DATE(order_purchase_timestamp),
                '%Y%m%d'
            ) + 0 AS date_key,

            DATE(order_purchase_timestamp) AS full_date,

            YEAR(order_purchase_timestamp) AS year,

            QUARTER(order_purchase_timestamp) AS quarter,

            MONTH(order_purchase_timestamp) AS month,

            MONTHNAME(order_purchase_timestamp) AS month_name,

            WEEK(order_purchase_timestamp, 3)
                AS week_of_year,

            DAY(order_purchase_timestamp)
                AS day_of_month,

            DAYOFWEEK(order_purchase_timestamp)
                AS day_of_week,

            DAYNAME(order_purchase_timestamp)
                AS day_name,

            CASE
                WHEN DAYOFWEEK(order_purchase_timestamp)
                     IN (1, 7)
                THEN TRUE
                ELSE FALSE
            END AS is_weekend

        FROM stg_orders

        WHERE order_purchase_timestamp IS NOT NULL;
    """)

    with engine.begin() as connection:
        connection.execute(query)

    print("[OK] dim_date completed")


def main():

    print("=" * 60)
    print("BUILDING ANALYTICS DIMENSIONS")
    print("=" * 60)

    engine = get_engine()

    # Build dimensions
    build_dim_customer(engine)
    build_dim_product(engine)
    build_dim_seller(engine)
    build_dim_geography(engine)
    build_dim_date(engine)

    print("\n" + "=" * 60)
    print("ALL DIMENSIONS BUILT SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()