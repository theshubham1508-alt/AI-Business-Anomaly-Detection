import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")


def generate_summary(df, dataset_name="dataset"):

    if df is None or df.empty:
        return "Dataset is empty."

    total_records = len(df)

    summary = f"""
AI BUSINESS ANOMALY DETECTION SYSTEM
====================================

DATASET: {dataset_name}

DATASET OVERVIEW
----------------
Total Records: {total_records}
Total Columns: {len(df.columns)}
Duplicate Records: {df.duplicated().sum()}
Missing Values: {df.isnull().sum().sum()}
"""

    # Anomaly analysis
    if "Anomaly" in df.columns:

        total_anomalies = int((df["Anomaly"] == -1).sum())
        normal_records = int((df["Anomaly"] == 1).sum())

        summary += f"""

ANOMALY ANALYSIS
----------------
Normal Records: {normal_records}
Total Anomalies: {total_anomalies}
Anomaly Percentage: {total_anomalies / total_records * 100:.2f}%
"""

    # Numerical analysis
    summary += "\nNUMERICAL ANALYSIS\n------------------\n"

    numeric_columns = df.select_dtypes(include=np.number).columns

    for column in numeric_columns:

        if column == "Anomaly":
            continue

        values = df[column].replace(
            [np.inf, -np.inf], np.nan
        ).dropna()

        if not values.empty:

            summary += f"""
{column}:
Average: {values.mean():.2f}
Minimum: {values.min():.2f}
Maximum: {values.max():.2f}
"""

    # Categorical analysis
    summary += "\nCATEGORICAL ANALYSIS\n--------------------\n"

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool", "str"]
    ).columns

    for column in categorical_columns:

        summary += f"\nTop values in {column}:\n"
        summary += df[column].value_counts().head(5).to_string()
        summary += "\n"

    # Save dataset-specific summary
    dataset_folder = os.path.join(REPORTS_FOLDER, dataset_name)
    os.makedirs(dataset_folder, exist_ok=True)

    summary_file = os.path.join(dataset_folder, "summary.txt")

    with open(summary_file, "w", encoding="utf-8") as file:
        file.write(summary)

    print("\nSummary Saved Successfully!")
    print(f"Location: {summary_file}")

    return summary