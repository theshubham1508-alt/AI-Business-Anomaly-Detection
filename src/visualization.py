import os
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")

SALES_GRAPH = os.path.join(REPORTS_FOLDER, "sales_by_region.png")
PROFIT_GRAPH = os.path.join(REPORTS_FOLDER, "profit_by_category.png")


def create_visualizations(df):

    # Create reports folder if not exists
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

    region_sales = df.groupby("Region")["Sales"].sum()

    plt.figure(figsize=(8, 5))
    region_sales.plot(kind="bar")

    plt.title("Sales by Region")
    plt.xlabel("Region")
    plt.ylabel("Sales")

    plt.tight_layout()
    plt.savefig(SALES_GRAPH)
    plt.close()

    category_profit = df.groupby("Category")["Profit"].sum()

    plt.figure(figsize=(8, 5))
    category_profit.plot(kind="bar")

    plt.title("Profit by Category")
    plt.xlabel("Category")
    plt.ylabel("Profit")

    plt.tight_layout()
    plt.savefig(PROFIT_GRAPH)
    plt.close()

    print("\nGraphs Saved Successfully!")
    print(f"Sales Graph  : {SALES_GRAPH}")
    print(f"Profit Graph : {PROFIT_GRAPH}")