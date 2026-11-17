import pandas as pd

file_path = "data/raw/ranked_match_data_kaggle.csv"

df = pd.read_csv(file_path)

print("\n===== NEW DATASET ANALYSIS =====")

print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns.tolist())

print("\nFirst 5 Records:")
print(df.head().to_string())

print("\nMissing Values:")
print(df.isnull().sum().sum())

print("\nDuplicate Records:")
print(df.duplicated().sum())

print("\nNumerical Columns:")
print(df.select_dtypes(include="number").columns.tolist())

print("\nDataset Check Completed!")