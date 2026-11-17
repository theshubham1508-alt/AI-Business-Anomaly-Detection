import os
import glob
import re

from data_loader import load_data
from data_cleaning import clean_data
from eda import perform_eda
from visualization import create_visualizations
from anomaly_detection import detect_anomalies
from ai_summary import generate_summary
from email_alert import send_email
from gemini_summary import generate_ai_summary


# PROJECT PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FOLDER = os.path.join(BASE_DIR, "data", "raw")


# SELECT CSV DATASET
def select_dataset():

    csv_files = glob.glob(os.path.join(RAW_FOLDER, "*.csv"))

    csv_files = [
        file for file in csv_files
        if not os.path.basename(file).startswith("~$")
    ]

    if not csv_files:
        print("No CSV dataset found in data/raw.")
        return None

    print("\nAVAILABLE DATASETS")
    print("-" * 40)

    for index, file in enumerate(csv_files, start=1):
        print(f"{index}. {os.path.basename(file)}")

    while True:
        try:
            choice = int(input("\nSelect dataset number: "))

            if 1 <= choice <= len(csv_files):
                return csv_files[choice - 1]

            print("Invalid selection. Try again.")

        except ValueError:
            print("Please enter a valid number.")


# MAIN AUTOMATION PIPELINE
def main():

    print("\n" + "=" * 60)
    print("AI BUSINESS ANOMALY DETECTION SYSTEM")
    print("=" * 60)

    # STEP 1: Select Dataset
    file_path = select_dataset()

    if file_path is None:
        return

    dataset_name = os.path.splitext(
        os.path.basename(file_path)
    )[0]

    dataset_name = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        dataset_name
    )

    print(f"\nSelected Dataset: {dataset_name}")

    # STEP 2: Load Dataset
    df = load_data(file_path)

    if df is None or df.empty:
        print("Dataset loading failed.")
        return

    # STEP 3: Clean Dataset
    df = clean_data(df, dataset_name)

    if df is None or df.empty:
        print("Data cleaning failed.")
        return

    # STEP 4: Exploratory Data Analysis
    perform_eda(df)

    # STEP 5: Generate Visualizations
    create_visualizations(df, dataset_name)

    # STEP 6: Detect Anomalies
    try:
        df = detect_anomalies(df, dataset_name)
    except ValueError as error:
        print(f"Anomaly detection failed: {error}")
        return

    # STEP 7: Generate Summary
    summary = generate_summary(df, dataset_name)

    # STEP 8: Gemini AI Analysis
    ai_summary = generate_ai_summary(
        summary,
        dataset_name
    )

    # STEP 9: Send Email
    send_email(ai_summary)

    print("\n" + "=" * 60)
    print("AUTOMATED ANALYSIS COMPLETED")
    print(f"Dataset: {dataset_name}")
    print("=" * 60)


if __name__ == "__main__":
    main()