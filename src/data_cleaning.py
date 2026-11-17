import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROCESSED_FOLDER = os.path.join(BASE_DIR, "data", "processed")


def clean_data(df, dataset_name="dataset"):

    print("\n" + "=" * 60)
    print("AUTOMATIC DATA CLEANING STARTED")
    print("=" * 60)

    if df is None or df.empty:
        print("Dataset is empty.")
        return df

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    # Remove duplicate records
    duplicate_count = df.duplicated().sum()
    print(f"Duplicate Rows Found: {duplicate_count}")
    df = df.drop_duplicates()

    # Handle infinite values
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    print("\nMissing Values Before Cleaning:")
    print(df.isnull().sum())

    # Detect date columns and standardize timezone
    for column in df.columns:

        if any(word in column.lower() for word in ["date", "time"]):

            converted = pd.to_datetime(
                df[column],
                format="mixed",
                errors="coerce",
                utc=True
            )

            if converted.notna().mean() >= 0.5:
                df[column] = converted.dt.tz_convert(None)
                print(f"Date Column Detected: {column}")

    # Fill numerical missing values
    numeric_columns = df.select_dtypes(include=np.number).columns

    for column in numeric_columns:
        median_value = df[column].median()

        if pd.notna(median_value):
            df[column] = df[column].fillna(median_value)

    # Fill categorical missing values
    categorical_columns = df.select_dtypes(
        include=["object", "category", "str"]
    ).columns

    for column in categorical_columns:
        mode_values = df[column].mode(dropna=True)

        if not mode_values.empty:
            df[column] = df[column].fillna(mode_values.iloc[0])
        else:
            df[column] = df[column].fillna("Unknown")

    # Dataset-specific folder
    dataset_folder = os.path.join(PROCESSED_FOLDER, dataset_name)
    os.makedirs(dataset_folder, exist_ok=True)

    cleaned_file = os.path.join(dataset_folder, "cleaned_data.csv")

    df.to_csv(cleaned_file, index=False)

    print("\nMissing Values After Cleaning:")
    print(df.isnull().sum())

    print("\nDATA CLEANING COMPLETED")
    print(f"Final Shape: {df.shape}")
    print(f"Saved: {cleaned_file}")

    return df