import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# MySQL configuration
# --------------------------------------------------

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")


# --------------------------------------------------
# Validate environment variables
# --------------------------------------------------

required_variables = {
    "MYSQL_HOST": MYSQL_HOST,
    "MYSQL_PORT": MYSQL_PORT,
    "MYSQL_DATABASE": MYSQL_DATABASE,
    "MYSQL_USER": MYSQL_USER,
    "MYSQL_PASSWORD": MYSQL_PASSWORD,
}

missing_variables = [
    name
    for name, value in required_variables.items()
    if value is None
]

if missing_variables:
    raise RuntimeError(
        f"Missing environment variables: {missing_variables}"
    )


# --------------------------------------------------
# Create MySQL engine
# --------------------------------------------------

def get_engine():

    database_url = URL.create(
        drivername="mysql+pymysql",
        username=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        database=MYSQL_DATABASE,
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    return engine


# --------------------------------------------------
# Test connection
# --------------------------------------------------

def test_connection():

    engine = get_engine()

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT DATABASE();")
        )

        database_name = result.scalar()

        print("==========================================")
        print("MYSQL CONNECTION SUCCESSFUL")
        print("==========================================")
        print(f"Host:     {MYSQL_HOST}")
        print(f"Port:     {MYSQL_PORT}")
        print(f"Database: {database_name}")
        print(f"User:     {MYSQL_USER}")
        print("==========================================")


# --------------------------------------------------
# Run test
# --------------------------------------------------

if __name__ == "__main__":
    test_connection()