
import getpass
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine, URL, text


def main():
    print("====================================")
    print(" E-COMMERCE PAYMENT ANALYSIS")
    print(" Python + Pandas + PostgreSQL")
    print("====================================")

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
        # Step 1: Read payment data from PostgreSQL
        query = text("""
            SELECT
                TRIM(payment_type) AS payment_type,
                TRIM(payment_value) AS payment_value
            FROM olist_order_payments_dataset
            WHERE TRIM(payment_value)
                  ~ '^[0-9]+([.][0-9]+)?$'
        """)

        with engine.connect() as connection:
            df = pd.read_sql_query(query, connection)

        print("\nPayment data loaded successfully!")
        print("Total records:", len(df))

        # Step 2: Convert payment values into numeric data
        df["payment_value"] = pd.to_numeric(
            df["payment_value"],
            errors="coerce"
        )

        df = df.dropna(subset=["payment_value"])

        # Step 3: Group payments by payment method
        analysis = (
            df.groupby("payment_type")
            .agg(
                total_transactions=("payment_value", "count"),
                total_payment=("payment_value", "sum"),
                average_payment=("payment_value", "mean")
            )
            .reset_index()
        )

        # Step 4: Calculate percentage contribution
        overall_payment = analysis["total_payment"].sum()

        analysis["payment_percentage"] = (
            analysis["total_payment"] /
            overall_payment * 100
        )

        analysis = analysis.round({
            "total_payment": 2,
            "average_payment": 2,
            "payment_percentage": 2
        })

        print("\n========== PAYMENT ANALYSIS ==========")
        print(analysis.to_string(index=False))

        print("\nTotal payment value:", round(overall_payment, 2))

        # Step 5: Create output folder
        output_dir = Path(__file__).resolve().parent / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Step 6: Export analysis to CSV
        csv_path = output_dir / "payment_analysis.csv"
        analysis.to_csv(csv_path, index=False)

        print("\nCSV saved:", csv_path)

        # Step 7: Create payment visualization
        chart_data = analysis.sort_values(
            "total_payment",
            ascending=True
        )

        plt.figure(figsize=(10, 6))

        plt.barh(
            chart_data["payment_type"],
            chart_data["total_payment"]
        )

        plt.title("E-Commerce Payment Method Analysis")
        plt.xlabel("Total Payment Value")
        plt.ylabel("Payment Method")
        plt.ticklabel_format(axis="x", style="plain")
        plt.tight_layout()

        chart_path = output_dir / "payment_methods_chart.png"

        plt.savefig(
            chart_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.show()

        print("\nChart saved:", chart_path)
        print("\nPAYMENT ANALYSIS COMPLETED!")

    except Exception as error:
        print("\nError:", error)

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
