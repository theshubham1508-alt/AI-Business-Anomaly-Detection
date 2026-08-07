import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")
SUMMARY_FILE = os.path.join(REPORTS_FOLDER, "summary.txt")


def generate_summary(df):

    total_records = len(df)
    total_anomalies = (df["Anomaly"] == -1).sum()
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    avg_sales = df["Sales"].mean()
    avg_profit = df["Profit"].mean()

    summary = f"""

Total Records      : {total_records}
Total Anomalies    : {total_anomalies}
Total Sales        : {total_sales:.2f}
Total Profit       : {total_profit:.2f}
Average Sales      : {avg_sales:.2f}
Average Profit     : {avg_profit:.2f}
"""

    print(summary)

    # Create reports folder if it doesn't exist
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

    # Save summary
    with open(SUMMARY_FILE, "w", encoding="utf-8") as file:
        file.write(summary)

    print("Summary Saved Successfully!")
    print(f"Location : {SUMMARY_FILE}")

    return summary