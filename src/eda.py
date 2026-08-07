import pandas as pd


def perform_eda(df):
    print("\n" + "=" * 60)
    print("EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    # Dataset Shape
    print("\nDataset Shape:")
    print(df.shape)

    # Data Types
    print("\nData Types:")
    print(df.dtypes)

    # Missing Values
    print("\nMissing Values:")
    print(df.isnull().sum())

    # Summary Statistics
    print("\nSummary Statistics:")
    print(df.describe())

    # Top Categories
    print("\nTop 10 Categories:")
    print(df["Category"].value_counts())

    # Top Regions
    print("\nSales by Region:")
    print(df.groupby("Region")["Sales"].sum())

    # Profit by Category
    print("\nProfit by Category:")
    print(df.groupby("Category")["Profit"].sum())