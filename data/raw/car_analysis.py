import pandas as pd

df = pd.read_csv("data/raw/car_prices.csv")

print("CAR BUSINESS ANALYSIS")

print("\nDataset Shape:")
print(df.shape)

print("\nFirst 5 Cars:")
print(df.head())

print("\nMissing Values:")
print(df.isnull().sum().sum())

print("\nAverage Selling Price:")
print(df["sellingprice"].mean())

print("\nAverage Market Value:")
print(df["mmr"].mean())

print("\nCar Brands:")
print(df["make"].value_counts().head(10))

print("\nAnalysis Completed!")