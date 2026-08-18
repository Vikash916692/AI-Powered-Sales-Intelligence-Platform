import sys
from pathlib import Path

# Ensure project root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
from sqlalchemy import text

from src.ingestion.database import get_engine


def build_fact_sales(engine):
    """
    Populate fact_sales from:
        stg_orders
        stg_order_items
        dim_customer
        dim_product
        dim_seller
        dim_geography
        dim_date

    Grain:
        One row = one order item
        (order_id, order_item_id)
    """

    print("\n" + "=" * 60)
    print("BUILDING FACT_SALES")
    print("=" * 60)

    query = text("""
        INSERT INTO fact_sales (
            order_id,
            order_item_id,

            customer_key,
            product_key,
            seller_key,

            purchase_date_key,

            customer_geography_key,
            seller_geography_key,

            order_status,

            price,
            freight_value,
            total_item_value,

            shipping_limit_date,
            delivered_date,
            estimated_delivery_date,

            delivery_days,
            delivery_delay_days,
            is_delayed,

            purchase_timestamp
        )

        SELECT

            oi.order_id,
            oi.order_item_id,

            c.customer_key,
            p.product_key,
            s.seller_key,

            d.date_key,

            cg.geography_key,
            sg.geography_key,

            o.order_status,

            oi.price,
            oi.freight_value,

            oi.price + oi.freight_value
                AS total_item_value,

            oi.shipping_limit_date,

            o.order_delivered_customer_date
                AS delivered_date,

            o.order_estimated_delivery_date
                AS estimated_delivery_date,

            CASE
                WHEN o.order_delivered_customer_date IS NOT NULL
                THEN DATEDIFF(
                    o.order_delivered_customer_date,
                    o.order_purchase_timestamp
                )
                ELSE NULL
            END AS delivery_days,

            CASE
                WHEN
                    o.order_delivered_customer_date IS NOT NULL
                    AND
                    o.order_estimated_delivery_date IS NOT NULL
                THEN DATEDIFF(
                    o.order_delivered_customer_date,
                    o.order_estimated_delivery_date
                )
                ELSE NULL
            END AS delivery_delay_days,

            CASE
                WHEN
                    o.order_delivered_customer_date IS NOT NULL
                    AND
                    o.order_estimated_delivery_date IS NOT NULL
                THEN
                    CASE
                        WHEN o.order_delivered_customer_date
                             >
                             o.order_estimated_delivery_date
                        THEN TRUE
                        ELSE FALSE
                    END
                ELSE NULL
            END AS is_delayed,

            o.order_purchase_timestamp

        FROM stg_order_items oi

        INNER JOIN stg_orders o
            ON oi.order_id = o.order_id

        INNER JOIN dim_customer c
            ON o.customer_id = c.customer_id

        INNER JOIN dim_product p
            ON oi.product_id = p.product_id

        INNER JOIN dim_seller s
            ON oi.seller_id = s.seller_id

        INNER JOIN dim_date d
            ON DATE(o.order_purchase_timestamp)
               = d.full_date

        LEFT JOIN dim_geography cg
            ON c.customer_zip_code_prefix
               = cg.zip_code_prefix

        LEFT JOIN dim_geography sg
            ON s.seller_zip_code_prefix
               = sg.zip_code_prefix

        ON DUPLICATE KEY UPDATE

            customer_key =
                VALUES(customer_key),

            product_key =
                VALUES(product_key),

            seller_key =
                VALUES(seller_key),

            purchase_date_key =
                VALUES(purchase_date_key),

            customer_geography_key =
                VALUES(customer_geography_key),

            seller_geography_key =
                VALUES(seller_geography_key),

            order_status =
                VALUES(order_status),

            price =
                VALUES(price),

            freight_value =
                VALUES(freight_value),

            total_item_value =
                VALUES(total_item_value),

            shipping_limit_date =
                VALUES(shipping_limit_date),

            delivered_date =
                VALUES(delivered_date),

            estimated_delivery_date =
                VALUES(estimated_delivery_date),

            delivery_days =
                VALUES(delivery_days),

            delivery_delay_days =
                VALUES(delivery_delay_days),

            is_delayed =
                VALUES(is_delayed),

            purchase_timestamp =
                VALUES(purchase_timestamp);
    """)

    with engine.begin() as connection:
        result = connection.execute(query)

        print(
            "[OK] Fact sales transformation completed"
        )

        print(
            f"Rows affected: {result.rowcount:,}"
        )


def validate_fact_sales(engine):
    """
    Basic validation of fact_sales.
    """

    print("\n" + "=" * 60)
    print("VALIDATING FACT_SALES")
    print("=" * 60)

    validations = {

        "Total rows": """
            SELECT COUNT(*)
            FROM fact_sales
        """,

        "Unique order items": """
            SELECT COUNT(*)
            FROM (
                SELECT
                    order_id,
                    order_item_id
                FROM fact_sales
                GROUP BY
                    order_id,
                    order_item_id
            ) x
        """,

        "Duplicate order items": """
            SELECT COUNT(*)
            FROM (
                SELECT
                    order_id,
                    order_item_id
                FROM fact_sales
                GROUP BY
                    order_id,
                    order_item_id
                HAVING COUNT(*) > 1
            ) x
        """,

        "Missing customers": """
            SELECT COUNT(*)
            FROM fact_sales
            WHERE customer_key IS NULL
        """,

        "Missing products": """
            SELECT COUNT(*)
            FROM fact_sales
            WHERE product_key IS NULL
        """,

        "Missing sellers": """
            SELECT COUNT(*)
            FROM fact_sales
            WHERE seller_key IS NULL
        """,

        "Missing purchase dates": """
            SELECT COUNT(*)
            FROM fact_sales
            WHERE purchase_date_key IS NULL
        """
    }

    with engine.connect() as connection:

        for name, query in validations.items():

            result = connection.execute(
                text(query)
            ).scalar()

            print(f"{name}: {result:,}")


def main():

    engine = get_engine()

    build_fact_sales(engine)

    validate_fact_sales(engine)

    print("\n" + "=" * 60)
    print("FACT_SALES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()