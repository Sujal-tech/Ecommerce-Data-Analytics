
import getpass
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine, URL, text


def main():
    print("========== MONTHLY REVENUE ANALYSIS ==========")

    password = getpass.getpass("Enter PostgreSQL password: ")

    url = URL.create(
        "postgresql+psycopg2",
        username="postgres",
        password=password,
        host="localhost",
        port=5432,
        database="ecommerce_analytics"
    )

    engine = create_engine(url)

    try:
        # 1. Read orders
        with engine.connect() as connection:

            orders = pd.read_sql_query(
                text("""
                    SELECT
                        order_id,
                        order_status,
                        order_purchase_timestamp
                    FROM olist_orders_dataset
                """),
                connection
            )

            # 2. Read order items
            items = pd.read_sql_query(
                text("""
                    SELECT
                        order_id,
                        price,
                        freight_value
                    FROM olist_order_items_dataset
                """),
                connection
            )

        print("Orders loaded:", len(orders))
        print("Order items loaded:", len(items))

        # 3. Remove possible CSV header rows
        orders = orders[
            orders["order_id"].str.strip().str.lower() != "order_id"
        ].copy()

        items = items[
            items["order_id"].str.strip().str.lower() != "order_id"
        ].copy()

        # 4. Convert columns to proper data types
        orders["purchase_date"] = pd.to_datetime(
            orders["order_purchase_timestamp"],
            errors="coerce"
        )

        items["price"] = pd.to_numeric(
            items["price"],
            errors="coerce"
        )

        items["freight_value"] = pd.to_numeric(
            items["freight_value"],
            errors="coerce"
        )

        # 5. Consider successfully delivered orders
        orders = orders[
            orders["order_status"].str.strip().str.lower() == "delivered"
        ]

        orders = orders.dropna(
            subset=["purchase_date"]
        )

        items = items.dropna(
            subset=["price"]
        )

        items["freight_value"] = items["freight_value"].fillna(0)

        # 6. Join orders and order items
        merged = pd.merge(
            orders[["order_id", "purchase_date"]],
            items[["order_id", "price", "freight_value"]],
            on="order_id",
            how="inner"
        )

        # 7. Calculate monthly revenue
        merged["sales_month"] = (
            merged["purchase_date"].dt.to_period("M").astype(str)
        )

        monthly = (
            merged.groupby("sales_month")
            .agg(
                total_orders=("order_id", "nunique"),
                product_revenue=("price", "sum"),
                shipping_charges=("freight_value", "sum")
            )
            .reset_index()
        )

        monthly["total_order_value"] = (
            monthly["product_revenue"] +
            monthly["shipping_charges"]
        )

        monthly["average_order_value"] = (
            monthly["total_order_value"] /
            monthly["total_orders"]
        )

        monthly = monthly.round(2)

        print("\n========== MONTHLY REVENUE RESULTS ==========")
        print(monthly.to_string(index=False))

        # 8. Create output folder
        output_dir = Path(__file__).resolve().parent / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 9. Save results to CSV
        csv_path = output_dir / "monthly_revenue_analysis.csv"
        monthly.to_csv(csv_path, index=False)

        print("\nCSV saved:", csv_path)

        # 10. Create monthly revenue chart
        plt.figure(figsize=(12, 6))

        plt.plot(
            monthly["sales_month"],
            monthly["total_order_value"],
            marker="o"
        )

        plt.title("Monthly E-Commerce Revenue")
        plt.xlabel("Month")
        plt.ylabel("Total Order Value")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        chart_path = output_dir / "monthly_revenue_chart.png"

        plt.savefig(
            chart_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.show()

        print("\nChart saved:", chart_path)
        print("\nMONTHLY REVENUE ANALYSIS COMPLETED!")

    except Exception as error:
        print("\nError:", error)

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
