import pandas as pd
import numpy as np


def perform_eda(df):
    print("\n" + "=" * 60)
    print("AUTOMATIC EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    if df is None or df.empty:
        print("Dataset is empty. EDA cannot be performed.")
        return

    # 1. Dataset Overview
    print("\n1. DATASET OVERVIEW")
    print("-" * 40)
    print(f"Total Rows: {df.shape[0]}")
    print(f"Total Columns: {df.shape[1]}")
    print(f"Total Cells: {df.size}")

    # 2. Column Information
    print("\n2. COLUMN INFORMATION")
    print("-" * 40)
    print(df.dtypes)

    # 3. Missing Values
    print("\n3. MISSING VALUES")
    print("-" * 40)

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        print("No missing values found.")
    else:
        print(missing)

    # 4. Duplicate Records
    print("\n4. DUPLICATE RECORDS")
    print("-" * 40)
    print(f"Duplicate Rows: {df.duplicated().sum()}")

    # 5. Numerical Analysis
    print("\n5. NUMERICAL ANALYSIS")
    print("-" * 40)

    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()

    if numeric_columns:
        print(df[numeric_columns].describe().round(2))
    else:
        print("No numerical columns found.")

    # 6. Categorical Analysis
    print("\n6. CATEGORICAL ANALYSIS")
    print("-" * 40)

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool", "str"]
    ).columns.tolist()

    if categorical_columns:
        for column in categorical_columns:
            print(f"\nTop 10 values in '{column}':")
            print(df[column].value_counts(dropna=False).head(10))
    else:
        print("No categorical columns found.")

    # 7. Date Analysis
    print("\n7. DATE ANALYSIS")
    print("-" * 40)

    date_columns = df.select_dtypes(
        include=["datetime", "datetimetz"]
    ).columns.tolist()

    # Automatically identify date-like object columns
    for column in categorical_columns:
        if any(word in column.lower() for word in ["date", "time"]):
            converted = pd.to_datetime(df[column], errors="coerce")
            if converted.notna().sum() > 0:
                date_columns.append(column)

    for column in set(date_columns):
        dates = pd.to_datetime(df[column], errors="coerce").dropna()

        if not dates.empty:
            print(f"\n{column}:")
            print(f"Earliest Date: {dates.min()}")
            print(f"Latest Date: {dates.max()}")

    # 8. Correlation Analysis
    print("\n8. CORRELATION ANALYSIS")
    print("-" * 40)

    if len(numeric_columns) >= 2:
        print(df[numeric_columns].corr().round(2))
    else:
        print("At least two numerical columns are required.")

    # 9. Automatic Business Insights
    print("\n9. AUTOMATIC DATASET INSIGHTS")
    print("-" * 40)

    print(f"Numerical Columns: {len(numeric_columns)}")
    print(f"Categorical Columns: {len(categorical_columns)}")
    print(f"Date Columns: {len(set(date_columns))}")

    for column in numeric_columns:
        values = df[column].dropna()

        if not values.empty:
            print(
                f"{column}: Average = {values.mean():.2f}, "
                f"Minimum = {values.min()}, "
                f"Maximum = {values.max()}"
            )

    print("\nAUTOMATIC EDA COMPLETED")
    print("=" * 60)