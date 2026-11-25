
import getpass
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine, URL, text


def main():
    print("========== PRODUCT CATEGORY ANALYSIS ==========")

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
        # 1. Load data from PostgreSQL
        with engine.connect() as connection:

            orders = pd.read_sql_query(
                text("""
                    SELECT order_id, order_status
                    FROM olist_orders_dataset
                """),
                connection
            )

            items = pd.read_sql_query(
                text("""
                    SELECT order_id, product_id, price
                    FROM olist_order_items_dataset
                """),
                connection
            )

            products = pd.read_sql_query(
                text("""
                    SELECT product_id, product_category_name
                    FROM olist_products_dataset
                """),
                connection
            )

            translations = pd.read_sql_query(
                text("""
                    SELECT product_category_name,
                           product_category_name_english
                    FROM product_category_name_translation
                """),
                connection
            )

        print("\nData loaded successfully!")

        # 2. Remove any imported CSV header rows
        orders = orders[
            orders["order_id"].astype("string").str.strip().str.lower()
            != "order_id"
        ].copy()

        items = items[
            items["order_id"].astype("string").str.strip().str.lower()
            != "order_id"
        ].copy()

        products = products[
            products["product_id"].astype("string").str.strip().str.lower()
            != "product_id"
        ].copy()

        translations = translations[
            translations["product_category_name"]
            .astype("string").str.strip().str.lower()
            != "product_category_name"
        ].copy()

        # 3. Convert price to numeric
        items["price"] = pd.to_numeric(
            items["price"],
            errors="coerce"
        )

        items = items.dropna(subset=["price", "product_id"])

        # 4. Select delivered orders only
        orders = orders[
            orders["order_status"].astype("string").str.strip().str.lower()
            == "delivered"
        ]

        # 5. Merge orders and order items
        data = pd.merge(
            items,
            orders[["order_id"]],
            on="order_id",
            how="inner"
        )

        # 6. Merge product information
        data = pd.merge(
            data,
            products,
            on="product_id",
            how="left"
        )

        # 7. Add English category names
        data = pd.merge(
            data,
            translations,
            on="product_category_name",
            how="left"
        )

        # 8. Use English category name where available
        data["category"] = (
            data["product_category_name_english"]
            .fillna(data["product_category_name"])
            .fillna("unknown")
            .astype(str)
            .str.strip()
        )

        data.loc[
            data["category"].eq(""),
            "category"
        ] = "unknown"

        # 9. Analyse product categories
        analysis = (
            data.groupby("category")
            .agg(
                total_items_sold=("product_id", "count"),
                total_orders=("order_id", "nunique"),
                total_revenue=("price", "sum"),
                average_item_price=("price", "mean")
            )
            .reset_index()
        )

        # 10. Sort by revenue and select top 10
        analysis = analysis.sort_values(
            "total_revenue",
            ascending=False
        ).head(10)

        analysis = analysis.round({
            "total_revenue": 2,
            "average_item_price": 2
        })

        print("\n========== TOP 10 PRODUCT CATEGORIES ==========")
        print(analysis.to_string(index=False))

        # 11. Create output folder
        output_dir = Path(__file__).resolve().parent / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 12. Export results
        csv_path = output_dir / "top_10_product_categories.csv"
        analysis.to_csv(csv_path, index=False)

        print("\nCSV saved:", csv_path)

        # 13. Create chart
        chart_data = analysis.sort_values(
            "total_revenue",
            ascending=True
        )

        plt.figure(figsize=(12, 7))

        plt.barh(
            chart_data["category"],
            chart_data["total_revenue"]
        )

        plt.title("Top 10 E-Commerce Product Categories by Revenue")
        plt.xlabel("Product Revenue")
        plt.ylabel("Product Category")
        plt.tight_layout()

        chart_path = output_dir / "top_10_product_categories.png"

        plt.savefig(
            chart_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.show()

        print("\nChart saved:", chart_path)
        print("\nPRODUCT CATEGORY ANALYSIS COMPLETED!")

    except Exception as error:
        print("\nError:", error)

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
