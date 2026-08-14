import sys
from pathlib import Path

# Ensure project root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from sqlalchemy import text

from src.ingestion.database import get_engine


def build_fact_reviews(engine):

    print("\n" + "=" * 60)
    print("BUILDING FACT_REVIEWS")
    print("=" * 60)

    query = text("""
        INSERT INTO fact_reviews (
            review_id,
            order_id,
            customer_key,
            review_date_key,
            review_score,
            review_comment_title,
            review_comment_message,
            review_creation_date,
            review_answer_timestamp
        )

        SELECT
            r.review_id,
            r.order_id,

            c.customer_key,

            d.date_key,

            r.review_score,
            r.review_comment_title,
            r.review_comment_message,
            r.review_creation_date,
            r.review_answer_timestamp

        FROM stg_reviews r

        LEFT JOIN stg_orders o
            ON r.order_id = o.order_id

        LEFT JOIN dim_customer c
            ON o.customer_id = c.customer_id

        LEFT JOIN dim_date d
            ON DATE(r.review_creation_date) = d.full_date

        ON DUPLICATE KEY UPDATE

            customer_key =
                VALUES(customer_key),

            review_date_key =
                VALUES(review_date_key),

            review_score =
                VALUES(review_score),

            review_comment_title =
                VALUES(review_comment_title),

            review_comment_message =
                VALUES(review_comment_message),

            review_creation_date =
                VALUES(review_creation_date),

            review_answer_timestamp =
                VALUES(review_answer_timestamp);
    """)

    with engine.begin() as connection:

        result = connection.execute(query)

        print("✓ fact_reviews transformation completed")
        print(f"Rows affected: {result.rowcount:,}")


def validate_fact_reviews(engine):

    print("\n" + "=" * 60)
    print("VALIDATING FACT_REVIEWS")
    print("=" * 60)

    validations = {

        "Total rows": """
            SELECT COUNT(*)
            FROM fact_reviews
        """,

        "Duplicate reviews": """
            SELECT COUNT(*)
            FROM (
                SELECT
                    review_id,
                    order_id
                FROM fact_reviews
                GROUP BY
                    review_id,
                    order_id
                HAVING COUNT(*) > 1
            ) x
        """,

        "Missing customer keys": """
            SELECT COUNT(*)
            FROM fact_reviews
            WHERE customer_key IS NULL
        """,

        "Missing review dates": """
            SELECT COUNT(*)
            FROM fact_reviews
            WHERE review_date_key IS NULL
        """,

        "Invalid review scores": """
            SELECT COUNT(*)
            FROM fact_reviews
            WHERE review_score NOT BETWEEN 1 AND 5
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

    build_fact_reviews(engine)

    validate_fact_reviews(engine)

    print("\n" + "=" * 60)
    print("FACT_REVIEWS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()