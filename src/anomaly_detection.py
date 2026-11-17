import os
import re
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_FOLDER = os.path.join(BASE_DIR, "data", "processed")


def detect_anomalies(df, dataset_name="dataset"):

    print("\n" + "=" * 60)
    print("AUTOMATIC ML ANOMALY DETECTION")
    print("=" * 60)

    if df is None or df.empty:
        print("Dataset is empty.")
        return df

    df = df.copy()

    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()

    excluded_words = [
        "id", "vin", "zip", "postal", "phone", "index"
    ]

    features = [
        col for col in numeric_columns
        if not any(word in col.lower() for word in excluded_words)
        and df[col].nunique(dropna=True) > 1
    ]

    if not features:
        print("No suitable numerical features found.")
        df["Anomaly"] = 1
        return df

    X = df[features].replace([np.inf, -np.inf], np.nan)

    # Remove all-empty columns
    features = [col for col in features if X[col].notna().any()]
    X = X[features]

    if not features:
        print("No valid numerical features found.")
        df["Anomaly"] = 1
        return df

    imputer = SimpleImputer(strategy="median")
    X_clean = imputer.fit_transform(X)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.02,
        random_state=42,
        n_jobs=-1
    )

    print(f"Selected Features: {features}")
    print("Training Isolation Forest...")

    predictions = model.fit_predict(X_clean)
    df["Anomaly"] = predictions

    anomaly_count = int((predictions == -1).sum())

    print(f"\nTotal Records: {len(df)}")
    print(f"Anomalies Found: {anomaly_count}")
    print(f"Anomaly Percentage: {anomaly_count / len(df) * 100:.2f}%")

    # Separate folder for each dataset
    dataset_folder = os.path.join(PROCESSED_FOLDER, dataset_name)
    os.makedirs(dataset_folder, exist_ok=True)

    anomaly_file = os.path.join(dataset_folder, "anomalies.csv")

    df[df["Anomaly"] == -1].to_csv(anomaly_file, index=False)

    print(f"\nAnomalies Saved: {anomaly_file}")

    return df