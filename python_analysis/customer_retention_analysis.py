
import getpass
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine, URL, text


def main():
    print("========== CUSTOMER RETENTION ANALYSIS ==========")

    password = getpass.getpass("Enter PostgreSQL password: ")

    url = URL.create(
        drivername="postgresql+psycopg2",
        username="postgres",
        password=password,
        host="localhost",
        port=5432,
        database="ecommerce_analytics"
    )

    engine = create_engine(url)

    try:
        # 1. Load customer and order data
        with engine.connect() as connection:

            customers = pd.read_sql_query(
                text("""
                    SELECT customer_id, customer_unique_id
                    FROM olist_customers_dataset
                """),
                connection
            )

            orders = pd.read_sql_query(
                text("""
                    SELECT
                        order_id,
                        customer_id,
                        order_status,
                        order_purchase_timestamp
                    FROM olist_orders_dataset
                """),
                connection
            )

        print("\nCustomer records loaded:", len(customers))
        print("Order records loaded:", len(orders))

        # 2. Remove CSV header rows and invalid IDs
        customers = customers[
            customers["customer_id"].astype("string").str.strip().str.lower()
            != "customer_id"
        ].copy()

        orders = orders[
            orders["order_id"].astype("string").str.strip().str.lower()
            != "order_id"
        ].copy()

        # 3. Clean customer identifiers
        for column in ["customer_id", "customer_unique_id"]:
            customers[column] = customers[column].astype("string").str.strip()

        for column in ["order_id", "customer_id", "order_status"]:
            orders[column] = orders[column].astype("string").str.strip()

        customers = customers.dropna(
            subset=["customer_id", "customer_unique_id"]
        )

        orders = orders.dropna(
            subset=["order_id", "customer_id"]
        )

        # 4. Consider delivered orders only
        orders = orders[
            orders["order_status"].str.lower() == "delivered"
        ].copy()

        # 5. Convert purchase date
        orders["purchase_date"] = pd.to_datetime(
            orders["order_purchase_timestamp"],
            errors="coerce"
        )

        orders = orders.dropna(subset=["purchase_date"])

        # 6. Remove duplicate order records
        orders = orders.drop_duplicates(subset=["order_id"])

        # 7. Connect orders with actual unique customers
        data = pd.merge(
            orders,
            customers[["customer_id", "customer_unique_id"]],
            on="customer_id",
            how="inner"
        )

        # 8. Calculate customer purchase frequency
        customer_analysis = (
            data.groupby("customer_unique_id")
            .agg(
                total_orders=("order_id", "nunique"),
                first_purchase=("purchase_date", "min"),
                last_purchase=("purchase_date", "max")
            )
            .reset_index()
        )

        # 9. Classify customers
        customer_analysis["customer_type"] = (
            customer_analysis["total_orders"]
            .apply(
                lambda count:
                "Repeat Customer" if count >= 2
                else "One-Time Customer"
            )
        )

        # 10. Calculate retention metrics
        total_customers = len(customer_analysis)

        repeat_customers = (
            customer_analysis["total_orders"] >= 2
        ).sum()

        one_time_customers = (
            customer_analysis["total_orders"] == 1
        ).sum()

        repeat_rate = (
            repeat_customers / total_customers * 100
            if total_customers else 0
        )

        average_orders = (
            customer_analysis["total_orders"].mean()
            if total_customers else 0
        )

        print("\n========== CUSTOMER METRICS ==========")
        print("Total customers:", total_customers)
        print("One-time customers:", one_time_customers)
        print("Repeat customers:", repeat_customers)
        print("Repeat purchase rate:", round(repeat_rate, 2), "%")
        print("Average orders per customer:", round(average_orders, 2))

        # 11. Find top 10 repeat customers
        top_customers = (
            customer_analysis[
                customer_analysis["total_orders"] >= 2
            ]
            .sort_values("total_orders", ascending=False)
            .head(10)
        )

        print("\n========== TOP 10 REPEAT CUSTOMERS ==========")
        print(top_customers.to_string(index=False))

        # 12. Create output folder
        output_dir = Path(__file__).resolve().parent / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 13. Export customer analysis
        customer_path = (
            output_dir / "customer_retention_analysis.csv"
        )

        customer_analysis.to_csv(
            customer_path,
            index=False
        )

        # 14. Export top customers
        top_path = output_dir / "top_10_repeat_customers.csv"

        top_customers.to_csv(
            top_path,
            index=False
        )

        # 15. Create customer retention chart
        labels = ["One-Time Customers", "Repeat Customers"]

        values = [one_time_customers, repeat_customers]

        plt.figure(figsize=(9, 6))

        plt.bar(labels, values)

        plt.title("Customer Repeat Purchase Analysis")
        plt.xlabel("Customer Type")
        plt.ylabel("Number of Customers")
        plt.tight_layout()

        chart_path = (
            output_dir / "customer_retention_chart.png"
        )

        plt.savefig(
            chart_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.show()

        print("\nCustomer analysis CSV saved:", customer_path)
        print("Top customers CSV saved:", top_path)
        print("Chart saved:", chart_path)

        print("\nCUSTOMER RETENTION ANALYSIS COMPLETED!")

    except Exception as error:
        print("\nError:", error)

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
