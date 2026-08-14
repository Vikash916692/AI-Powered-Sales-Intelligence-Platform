import sys
from pathlib import Path

# Ensure project root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
from sqlalchemy import text

from src.ingestion.database import get_engine


def build_fact_payments(engine):

    print("\n" + "=" * 60)
    print("BUILDING FACT_PAYMENTS")
    print("=" * 60)

    query = text("""
        INSERT INTO fact_payments (
            order_id,
            payment_sequential,
            customer_key,
            payment_type,
            payment_installments,
            payment_value
        )

        SELECT
            p.order_id,
            p.payment_sequential,

            c.customer_key,

            p.payment_type,
            p.payment_installments,
            p.payment_value

        FROM stg_payments p

        LEFT JOIN stg_orders o
            ON p.order_id = o.order_id

        LEFT JOIN dim_customer c
            ON o.customer_id = c.customer_id

        ON DUPLICATE KEY UPDATE

            customer_key =
                VALUES(customer_key),

            payment_type =
                VALUES(payment_type),

            payment_installments =
                VALUES(payment_installments),

            payment_value =
                VALUES(payment_value);
    """)

    with engine.begin() as connection:

        result = connection.execute(query)

        print("✓ fact_payments transformation completed")
        print(f"Rows affected: {result.rowcount:,}")


def validate_fact_payments(engine):

    print("\n" + "=" * 60)
    print("VALIDATING FACT_PAYMENTS")
    print("=" * 60)

    validations = {

        "Total rows": """
            SELECT COUNT(*)
            FROM fact_payments
        """,

        "Duplicate payment records": """
            SELECT COUNT(*)
            FROM (
                SELECT
                    order_id,
                    payment_sequential
                FROM fact_payments
                GROUP BY
                    order_id,
                    payment_sequential
                HAVING COUNT(*) > 1
            ) x
        """,

        "Missing customer keys": """
            SELECT COUNT(*)
            FROM fact_payments
            WHERE customer_key IS NULL
        """,

        "Negative payment values": """
            SELECT COUNT(*)
            FROM fact_payments
            WHERE payment_value < 0
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

    build_fact_payments(engine)

    validate_fact_payments(engine)

    print("\n" + "=" * 60)
    print("FACT_PAYMENTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()