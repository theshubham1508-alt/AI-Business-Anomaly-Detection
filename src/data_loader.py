import pandas as pd

def load_data(file_path):
    try:
        df = pd.read_csv(file_path)

        print("=" * 50)
        print("Dataset Loaded Successfully")
        print("=" * 50)

        print(f"Rows    : {df.shape[0]}")
        print(f"Columns : {df.shape[1]}")

        print("\nColumns:")
        print(df.columns.tolist())

        return df

    except Exception as e:
        print(f"Error: {e}")
        return None