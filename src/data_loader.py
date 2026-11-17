import os
import pandas as pd


def load_data(file_path):

    print("\n" + "=" * 60)
    print("AUTOMATIC DATASET LOADING")
    print("=" * 60)

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    if not file_path.lower().endswith(".csv"):
        print("Unsupported file format. Please provide a CSV file.")
        return None

    # Try different encodings and automatically detect separator
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]

    for encoding in encodings:
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                sep=None,
                engine="python",
                on_bad_lines="error"
            )

            if df.empty or len(df.columns) < 1:
                print("Dataset is empty or invalid.")
                return None

            # Clean column names
            df.columns = df.columns.astype(str).str.strip()

            if df.columns.duplicated().any():
                print("Duplicate column names detected.")
                return None

            print("\nDataset Loaded Successfully!")
            print(f"File Name : {os.path.basename(file_path)}")
            print(f"Encoding  : {encoding}")
            print(f"Rows      : {df.shape[0]}")
            print(f"Columns   : {df.shape[1]}")

            print("\nColumn Names:")
            print(df.columns.tolist())

            return df

        except UnicodeDecodeError:
            continue

        except Exception as e:
            print(f"Loading attempt failed: {e}")
            return None

    print("Unable to read dataset with supported encodings.")
    return None