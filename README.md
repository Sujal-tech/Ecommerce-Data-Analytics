# Brazilian E-Commerce Data Analytics

## Project Overview
An end-to-end data analytics project using PostgreSQL, Python, Pandas and Microsoft Power BI to analyse Brazilian e-commerce sales, customer behaviour, product categories, payment methods and delivery performance.

## Technologies
- PostgreSQL and SQL
- Python
- Pandas
- Matplotlib
- Microsoft Power BI
- Git and GitHub

## Dataset
Brazilian E-Commerce Public Dataset by Olist, downloaded from Kaggle.

The dataset contains nine related datasets covering customers, orders, order items, payments, reviews, products, sellers, geolocation and product category translation.

## Project Analysis

### SQL
- Database and table creation
- Data validation and cleaning
- Payment method analysis
- Monthly revenue analysis
- Product category analysis
- Delivery performance
- Customer repeat-purchase analysis

### Python
- Payment analysis using Pandas
- Monthly revenue analysis
- Top 10 product category analysis
- Customer retention analysis
- Matplotlib visualizations

### Power BI Dashboard
- Total Revenue
- Total Delivered Orders
- Total Customers
- Average Order Value
- Monthly Revenue Trend
- Top 10 Product Categories
- Revenue by Payment Method
- On-Time Delivery Performance
- Top 10 States by Revenue
- Interactive date and state filters

## Project Structure

```text
Ecommerce-Data-Analytics/
│
├── python_analysis/
│   ├── test_connection.py
│   ├── payment_analysis.py
│   ├── monthly_revenue_analysis.py
│   ├── product_category_analysis.py
│   └── customer_retention_analysis.py
│
├── Documentation/
├── sql_queries/
├── powerbi/
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Python Installation

Install the required libraries:

```bash
pip install pandas sqlalchemy psycopg2-binary matplotlib
```

## Running the Analysis

```bash
python python_analysis/payment_analysis.py
python python_analysis/monthly_revenue_analysis.py
python python_analysis/product_category_analysis.py
python python_analysis/customer_retention_analysis.py
```

PostgreSQL must be configured with the database and tables used by the Python scripts.

## Business Outcomes

The project demonstrates how SQL, Python and Power BI can be used to transform e-commerce transaction data into business insights and interactive visual reports.

**Note:** Revenue represents product selling value, not net profit. The original dataset contains Brazilian transactions and uses Brazilian reais (BRL).
