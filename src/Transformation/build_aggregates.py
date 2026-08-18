import sys
from pathlib import Path

# Ensure project root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from sqlalchemy import text

from src.ingestion.database import get_engine

# ============================================================
# 1. DAILY SALES
# ============================================================

def build_daily_sales(engine):

    print("\nBuilding agg_daily_sales...")

    query = text("""
        INSERT INTO agg_daily_sales (
            date_key,
            order_count,
            item_count,
            revenue,
            freight_revenue,
            total_sales_value,
            average_order_value,
            average_item_value
        )

        SELECT
            fs.purchase_date_key,

            COUNT(DISTINCT fs.order_id),

            COUNT(*),

            ROUND(SUM(fs.price), 2),

            ROUND(SUM(fs.freight_value), 2),

            ROUND(SUM(fs.total_item_value), 2),

            ROUND(
                SUM(fs.total_item_value)
                / COUNT(DISTINCT fs.order_id),
                2
            ),

            ROUND(
                SUM(fs.total_item_value)
                / COUNT(*),
                2
            )

        FROM fact_sales fs

        GROUP BY fs.purchase_date_key

        ON DUPLICATE KEY UPDATE

            order_count = VALUES(order_count),
            item_count = VALUES(item_count),
            revenue = VALUES(revenue),
            freight_revenue = VALUES(freight_revenue),
            total_sales_value = VALUES(total_sales_value),
            average_order_value = VALUES(average_order_value),
            average_item_value = VALUES(average_item_value);
    """)

    with engine.begin() as connection:
        result = connection.execute(query)

    print(f"✓ agg_daily_sales: {result.rowcount:,} rows")


# ============================================================
# 2. PRODUCT PERFORMANCE
# ============================================================

def build_product_performance(engine):

    print("\nBuilding agg_product_performance...")

    query = text("""
        INSERT INTO agg_product_performance (
            product_key,
            order_count,
            item_count,
            revenue,
            freight_revenue,
            average_price,
            late_order_count,
            late_delivery_rate
        )

        SELECT

            product_key,

            COUNT(DISTINCT order_id),

            COUNT(*),

            ROUND(
                SUM(total_item_value),
                2
            ),

            ROUND(
                SUM(freight_value),
                2
            ),

            ROUND(
                AVG(price),
                2
            ),

            SUM(
                CASE
                    WHEN is_delayed = TRUE
                    THEN 1
                    ELSE 0
                END
            ),

            ROUND(
                AVG(
                    CASE
                        WHEN delivered_date IS NOT NULL
                        THEN is_delayed
                    END
                ),
                4
            )

        FROM fact_sales

        GROUP BY product_key

        ON DUPLICATE KEY UPDATE

            order_count = VALUES(order_count),
            item_count = VALUES(item_count),
            revenue = VALUES(revenue),
            freight_revenue = VALUES(freight_revenue),
            average_price = VALUES(average_price),
            late_order_count = VALUES(late_order_count),
            late_delivery_rate = VALUES(late_delivery_rate);
    """)

    with engine.begin() as connection:
        result = connection.execute(query)

    print(
        f"✓ agg_product_performance: "
        f"{result.rowcount:,} rows"
    )


# ============================================================
# 3. CUSTOMER PERFORMANCE
# ============================================================

def build_customer_performance(engine):

    print("\nBuilding agg_customer_performance...")

    query = text("""
        INSERT INTO agg_customer_performance (
            customer_key,
            order_count,
            item_count,
            total_revenue,
            average_order_value,
            first_order_date,
            last_order_date,
            review_count,
            average_review_score,
            late_order_count,
            late_delivery_rate
        )

        SELECT

            s.customer_key,

            s.order_count,
            s.item_count,
            s.total_revenue,
            s.average_order_value,
            s.first_order_date,
            s.last_order_date,

            COALESCE(r.review_count, 0),

            r.average_review_score,

            s.late_order_count,
            s.late_delivery_rate

        FROM (

            SELECT

                customer_key,

                COUNT(DISTINCT order_id)
                    AS order_count,

                COUNT(*)
                    AS item_count,

                ROUND(
                    SUM(total_item_value),
                    2
                ) AS total_revenue,

                ROUND(
                    SUM(total_item_value)
                    / COUNT(DISTINCT order_id),
                    2
                ) AS average_order_value,

                MIN(
                    DATE(purchase_timestamp)
                ) AS first_order_date,

                MAX(
                    DATE(purchase_timestamp)
                ) AS last_order_date,

                SUM(
                    CASE
                        WHEN is_delayed = TRUE
                        THEN 1
                        ELSE 0
                    END
                ) AS late_order_count,

                ROUND(
                    AVG(
                        CASE
                            WHEN delivered_date IS NOT NULL
                            THEN is_delayed
                        END
                    ),
                    4
                ) AS late_delivery_rate

            FROM fact_sales

            GROUP BY customer_key

        ) s

        LEFT JOIN (

            SELECT

                customer_key,

                COUNT(*) AS review_count,

                ROUND(
                    AVG(review_score),
                    2
                ) AS average_review_score

            FROM fact_reviews

            GROUP BY customer_key

        ) r

            ON s.customer_key = r.customer_key

        ON DUPLICATE KEY UPDATE

            order_count = VALUES(order_count),
            item_count = VALUES(item_count),
            total_revenue = VALUES(total_revenue),
            average_order_value = VALUES(average_order_value),
            first_order_date = VALUES(first_order_date),
            last_order_date = VALUES(last_order_date),
            review_count = VALUES(review_count),
            average_review_score = VALUES(average_review_score),
            late_order_count = VALUES(late_order_count),
            late_delivery_rate = VALUES(late_delivery_rate);
    """)

    with engine.begin() as connection:
        result = connection.execute(query)

    print(
        f"✓ agg_customer_performance: "
        f"{result.rowcount:,} rows"
    )


# ============================================================
# 4. SELLER PERFORMANCE
# ============================================================

def build_seller_performance(engine):

    print("\nBuilding agg_seller_performance...")

    query = text("""
        INSERT INTO agg_seller_performance (
            seller_key,
            order_count,
            item_count,
            total_revenue,
            average_order_value,
            average_delivery_days,
            late_order_count,
            late_delivery_rate,
            review_count,
            average_review_score
        )

        SELECT

            s.seller_key,

            s.order_count,
            s.item_count,
            s.total_revenue,
            s.average_order_value,
            s.average_delivery_days,
            s.late_order_count,
            s.late_delivery_rate,

            COALESCE(r.review_count, 0),

            r.average_review_score

        FROM (

            SELECT

                seller_key,

                COUNT(DISTINCT order_id)
                    AS order_count,

                COUNT(*)
                    AS item_count,

                ROUND(
                    SUM(total_item_value),
                    2
                ) AS total_revenue,

                ROUND(
                    SUM(total_item_value)
                    / COUNT(DISTINCT order_id),
                    2
                ) AS average_order_value,

                ROUND(
                    AVG(delivery_days),
                    2
                ) AS average_delivery_days,

                SUM(
                    CASE
                        WHEN is_delayed = TRUE
                        THEN 1
                        ELSE 0
                    END
                ) AS late_order_count,

                ROUND(
                    AVG(
                        CASE
                            WHEN delivered_date IS NOT NULL
                            THEN is_delayed
                        END
                    ),
                    4
                ) AS late_delivery_rate

            FROM fact_sales

            GROUP BY seller_key

        ) s

        LEFT JOIN (

            /*
                IMPORTANT:
                Reviews are deduplicated at
                (review_id, order_id) before
                associating them with sellers.
            */

            SELECT

                x.seller_key,

                COUNT(*) AS review_count,

                ROUND(
                    AVG(x.review_score),
                    2
                ) AS average_review_score

            FROM (

                SELECT DISTINCT

                    fs.seller_key,
                    fr.review_id,
                    fr.order_id,
                    fr.review_score

                FROM fact_reviews fr

                INNER JOIN fact_sales fs
                    ON fr.order_id = fs.order_id

            ) x

            GROUP BY x.seller_key

        ) r

            ON s.seller_key = r.seller_key

        ON DUPLICATE KEY UPDATE

            order_count = VALUES(order_count),
            item_count = VALUES(item_count),
            total_revenue = VALUES(total_revenue),
            average_order_value = VALUES(average_order_value),
            average_delivery_days = VALUES(average_delivery_days),
            late_order_count = VALUES(late_order_count),
            late_delivery_rate = VALUES(late_delivery_rate),
            review_count = VALUES(review_count),
            average_review_score = VALUES(average_review_score);
    """)

    with engine.begin() as connection:
        result = connection.execute(query)

    print(
        f"✓ agg_seller_performance: "
        f"{result.rowcount:,} rows"
    )


# ============================================================
# 5. GEOGRAPHY PERFORMANCE
# ============================================================

def build_geography_performance(engine):

    print("\nBuilding agg_geography_performance...")

    query = text("""
        INSERT INTO agg_geography_performance (
            state,
            order_count,
            item_count,
            total_revenue,
            average_order_value,
            average_delivery_days,
            late_order_count,
            late_delivery_rate,
            average_review_score,
            review_count
        )

        SELECT

            s.state,

            s.order_count,
            s.item_count,
            s.total_revenue,
            s.average_order_value,
            s.average_delivery_days,
            s.late_order_count,
            s.late_delivery_rate,

            r.average_review_score,
            COALESCE(r.review_count, 0)

        FROM (

            SELECT

                dg.state,

                COUNT(DISTINCT fs.order_id)
                    AS order_count,

                COUNT(*)
                    AS item_count,

                ROUND(
                    SUM(fs.total_item_value),
                    2
                ) AS total_revenue,

                ROUND(
                    SUM(fs.total_item_value)
                    / COUNT(DISTINCT fs.order_id),
                    2
                ) AS average_order_value,

                ROUND(
                    AVG(fs.delivery_days),
                    2
                ) AS average_delivery_days,

                SUM(
                    CASE
                        WHEN fs.is_delayed = TRUE
                        THEN 1
                        ELSE 0
                    END
                ) AS late_order_count,

                ROUND(
                    AVG(
                        CASE
                            WHEN fs.delivered_date IS NOT NULL
                            THEN fs.is_delayed
                        END
                    ),
                    4
                ) AS late_delivery_rate

            FROM fact_sales fs

            INNER JOIN dim_geography dg
                ON fs.customer_geography_key =
                   dg.geography_key

            GROUP BY dg.state

        ) s

        LEFT JOIN (

            SELECT

                x.state,

                COUNT(*) AS review_count,

                ROUND(
                    AVG(x.review_score),
                    2
                ) AS average_review_score

            FROM (

                /*
                    One review contributes once
                    to the customer's geography.
                */

                SELECT DISTINCT

                    dg.state,
                    fr.review_id,
                    fr.order_id,
                    fr.review_score

                FROM fact_reviews fr

                INNER JOIN fact_sales fs
                    ON fr.order_id = fs.order_id

                INNER JOIN dim_geography dg
                    ON fs.customer_geography_key =
                       dg.geography_key

            ) x

            GROUP BY x.state

        ) r

            ON s.state = r.state

        ON DUPLICATE KEY UPDATE

            order_count = VALUES(order_count),
            item_count = VALUES(item_count),
            total_revenue = VALUES(total_revenue),
            average_order_value = VALUES(average_order_value),
            average_delivery_days = VALUES(average_delivery_days),
            late_order_count = VALUES(late_order_count),
            late_delivery_rate = VALUES(late_delivery_rate),
            average_review_score = VALUES(average_review_score),
            review_count = VALUES(review_count);
    """)

    with engine.begin() as connection:
        result = connection.execute(query)

    print(
        f"✓ agg_geography_performance: "
        f"{result.rowcount:,} rows"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 60)
    print("BUILDING AGGREGATE TABLES")
    print("=" * 60)

    engine = get_engine()

    build_daily_sales(engine)

    build_product_performance(engine)

    build_customer_performance(engine)

    build_seller_performance(engine)

    build_geography_performance(engine)

    print("\n" + "=" * 60)
    print("ALL AGGREGATE TABLES BUILT SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()