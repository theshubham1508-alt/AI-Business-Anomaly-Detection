import os
import pandas as pd


# Project Root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Output Folder
PROCESSED_FOLDER = os.path.join(BASE_DIR, "data", "processed")

# Output File
CLEANED_FILE = os.path.join(PROCESSED_FOLDER, "cleaned_data.csv")


def clean_data(df):

    print("\n" + "=" * 50)
    print("DATA CLEANING STARTED")
    print("=" * 50)

    # Duplicate Rows
    duplicate_count = df.duplicated().sum()
    print(f"\nDuplicate Rows Found : {duplicate_count}")

    df = df.drop_duplicates()

    # Missing Values
    print("\nMissing Values:")
    print(df.isnull().sum())

    # Date Conversion
    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        format="mixed",
        errors="coerce"
    )

    df["Ship Date"] = pd.to_datetime(
        df["Ship Date"],
        format="mixed",
        errors="coerce"
    )

    print("\nData Cleaning Completed Successfully")

    # Create folder if not exists
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)

    # Save cleaned dataset
    df.to_csv(CLEANED_FILE, index=False)

    print("\nCleaned Dataset Saved Successfully!")
    print(f"Location : {CLEANED_FILE}")

    return df