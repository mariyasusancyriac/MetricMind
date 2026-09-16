import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.dirname(__file__)
RAW_PATH = os.path.join(DATA_DIR, "raw_kaggle_data.csv")
CLEAN_PATH = os.path.join(DATA_DIR, "enterprise_data.csv")

def clean_dataset():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(f"Missing {RAW_PATH}. Place your Kaggle CSV in data/raw_kaggle_data.csv")

    try:
        df = pd.read_csv(RAW_PATH, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(RAW_PATH, encoding="windows-1252")

    # Rename Kaggle column headers to enterprise schema
    mapping = {
        "Order ID": "transaction_id",
        "Region": "region",
        "Category": "product_line",
        "Sales": "gross_revenue",
        "Profit": "net_margin",
        "Quantity": "units_sold"
    }
    df = df.rename(columns=mapping)

    # Standardize Fiscal Quarter
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"])
        df["quarter"] = df["Order Date"].dt.year.astype(str) + "-Q" + df["Order Date"].dt.quarter.astype(str)
    else:
        df["quarter"] = "2025-Q4"

    # Financial Metric Derivations
    df["gross_revenue"] = df["gross_revenue"].round(2)
    df["net_margin"] = df["net_margin"].round(2)
    df["cogs"] = (df["gross_revenue"] - df["net_margin"]).apply(lambda x: max(round(x * 0.70, 2), 0.0))
    df["operating_expense"] = (df["gross_revenue"] - df["cogs"] - df["net_margin"]).apply(lambda x: max(round(x, 2), 0.0))
    df["unit_price"] = (df["gross_revenue"] / df["units_sold"].replace(0, 1)).round(2)

    # Filter essential columns
    required = [
        "transaction_id", "quarter", "region", "product_line",
        "units_sold", "unit_price", "gross_revenue", "cogs",
        "operating_expense", "net_margin"
    ]
    df_clean = df[[c for c in required if c in df.columns]].dropna()
    df_clean.to_csv(CLEAN_PATH, index=False)
    print(f"ETL Complete: Generated {CLEAN_PATH} with {len(df_clean)} records.")

if __name__ == "__main__":
    clean_dataset()