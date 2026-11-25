
import getpass
import pandas as pd

from sqlalchemy import create_engine, URL, text
from sqlalchemy.exc import SQLAlchemyError


def main():
    print("====================================")
    print(" E-COMMERCE DATA ANALYTICS PROJECT")
    print(" PostgreSQL + Python Connection")
    print("====================================")

    # Ask for PostgreSQL password securely
    password = getpass.getpass("Enter PostgreSQL password: ")

    # PostgreSQL connection details
    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username="postgres",
        password=password,
        host="localhost",
        port=5432,
        database="ecommerce_analytics"
    )

    # Create database connection
    engine = create_engine(connection_url)

    try:
        with engine.connect() as connection:

            # 1. Check database connection
            database_name = connection.execute(
                text("SELECT current_database()")
            ).scalar_one()

            print("\nSUCCESS: PostgreSQL connected!")
            print("Database:", database_name)

            # 2. Display customer data
            print("\n========== CUSTOMER DATA ==========")

            customer_query = text("""
                SELECT
                    customer_id,
                    customer_unique_id,
                    customer_city,
                    customer_state
                FROM olist_customers_dataset
                LIMIT 10
            """)

            customers = pd.read_sql_query(
                customer_query,
                connection
            )

            print(customers.to_string(index=False))

            # 3. Count total customer records
            total_customers = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM olist_customers_dataset
                """)
            ).scalar_one()

            print("\nTotal customer records:", total_customers)

            # 4. Count all imported tables
            print("\n========== DATABASE TABLES ==========")

            tables_query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)

            tables = pd.read_sql_query(
                tables_query,
                connection
            )

            print(tables.to_string(index=False))
            print("\nTotal tables:", len(tables))

            print("\n====================================")
            print(" PYTHON ANALYSIS CONNECTION SUCCESS!")
            print("====================================")

    except SQLAlchemyError as error:
        print("\nDATABASE CONNECTION ERROR:")
        print(error)

    except Exception as error:
        print("\nERROR:")
        print(error)

    finally:
        engine.dispose()
        print("\nDatabase connection closed.")


if __name__ == "__main__":
    main()
