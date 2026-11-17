import os
import re
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")


def create_visualizations(df, dataset_name="dataset"):

    print("\n" + "=" * 60)
    print("DATASET-WISE AUTOMATIC VISUALIZATION")
    print("=" * 60)

    if df is None or df.empty:
        print("No data available.")
        return []

    # Separate graph folder for every dataset
    graph_folder = os.path.join(
        REPORTS_FOLDER, dataset_name, "graphs"
    )
    os.makedirs(graph_folder, exist_ok=True)

    saved_graphs = []

    def safe_filename(name):
        return re.sub(r"[^a-zA-Z0-9_]", "_", str(name).lower())

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    # Numerical distribution
    for column in numeric_columns[:8]:

        values = df[column].dropna()

        if values.empty or values.nunique() < 2:
            continue

        plt.figure(figsize=(8, 5))
        plt.hist(values, bins=30, edgecolor="black")

        plt.title(f"Distribution of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.tight_layout()

        path = os.path.join(
            graph_folder,
            f"{safe_filename(column)}_distribution.png"
        )

        plt.savefig(path)
        plt.close()
        saved_graphs.append(path)

    # Categorical frequency
    for column in categorical_columns[:5]:

        values = df[column].value_counts().head(10)

        if values.empty:
            continue

        plt.figure(figsize=(9, 5))
        values.plot(kind="bar")

        plt.title(f"Top Categories in {column}")
        plt.xlabel(column)
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        path = os.path.join(
            graph_folder,
            f"{safe_filename(column)}_categories.png"
        )

        plt.savefig(path)
        plt.close()
        saved_graphs.append(path)

    # Correlation heatmap
    if len(numeric_columns) >= 2:

        correlation = df[numeric_columns].corr()

        plt.figure(figsize=(10, 7))
        plt.imshow(correlation, cmap="coolwarm", aspect="auto")
        plt.colorbar(label="Correlation")

        plt.xticks(
            range(len(numeric_columns)),
            numeric_columns,
            rotation=90
        )

        plt.yticks(
            range(len(numeric_columns)),
            numeric_columns
        )

        plt.title("Numerical Feature Correlation")
        plt.tight_layout()

        path = os.path.join(
            graph_folder, "correlation_heatmap.png"
        )

        plt.savefig(path)
        plt.close()
        saved_graphs.append(path)

    # Anomaly visualization
    if "Anomaly" in df.columns and numeric_columns:

        feature = numeric_columns[0]

        plt.figure(figsize=(8, 5))
        df.boxplot(column=feature, by="Anomaly")

        plt.title(f"{feature} Distribution by Anomaly Status")
        plt.suptitle("")
        plt.xlabel("Anomaly Status")
        plt.ylabel(feature)
        plt.tight_layout()

        path = os.path.join(
            graph_folder, "anomaly_distribution.png"
        )

        plt.savefig(path)
        plt.close()
        saved_graphs.append(path)

    print(f"\nTotal Graphs Created: {len(saved_graphs)}")

    for graph in saved_graphs:
        print(f"Saved: {graph}")

    return saved_graphs