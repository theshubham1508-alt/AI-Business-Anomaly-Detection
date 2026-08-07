import os
from sklearn.ensemble import IsolationForest


# ==============================
# Project Paths
# ==============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROCESSED_FOLDER = os.path.join(BASE_DIR, "data", "processed")
ANOMALY_FILE = os.path.join(PROCESSED_FOLDER, "anomalies.csv")


def detect_anomalies(df):

    print("\n" + "=" * 60)
    print("ANOMALY DETECTION")
    print("=" * 60)

    # Features used for anomaly detection
    features = df[["Sales", "Profit", "Quantity", "Discount"]]

    # Isolation Forest Model
    model = IsolationForest(
        n_estimators=100,
        contamination=0.02,
        random_state=42
    )

    # Train model & predict anomalies
    df["Anomaly"] = model.fit_predict(features)

    # Count anomalies
    anomaly_count = (df["Anomaly"] == -1).sum()

    print(f"\nTotal Anomalies Found : {anomaly_count}")

    # Filter anomalies
    anomalies = df[df["Anomaly"] == -1]

    # Create folder if it doesn't exist
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)

    # Save anomalies
    anomalies.to_csv(
        ANOMALY_FILE,
        index=False
    )

    print("\nAnomalies Saved Successfully!")
    print(f"Location : {ANOMALY_FILE}")

    return df