import os

from data_loader import load_data
from data_cleaning import clean_data
from eda import perform_eda
from visualization import create_visualizations
from anomaly_detection import detect_anomalies
from ai_summary import generate_summary
from email_alert import send_email
from gemini_summary import generate_ai_summary
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "business_data.csv"
)


def main():

    # Load Dataset
    df = load_data(FILE_PATH)

    if df is None:
        print("Dataset could not be loaded.")
        return

    # Data Cleaning
    df = clean_data(df)

    print("\nFirst 5 Rows After Cleaning:\n")
    print(df.head())

    # Exploratory Data Analysis
    perform_eda(df)

    # Visualizations
    create_visualizations(df)

    # Anomaly Detection
    df = detect_anomalies(df)

    # AI Summary
    summary = generate_summary(df)
    ai_summary = generate_ai_summary(summary)

    print("\n===== DEBUG =====")
    print(type(summary))
    print(summary)

    # Email Alert
    send_email(ai_summary)


if __name__ == "__main__":
    main()