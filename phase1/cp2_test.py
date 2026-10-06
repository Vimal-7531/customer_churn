import pandas as pd

from customer_cleaner import CustomerCleaner

df = pd.read_csv("customer_churn.csv")

print("BEFORE CLEANING")
print(df.shape)
print(df.dtypes)

cleaner = CustomerCleaner(df)

clean_df = cleaner.clean()

print("\nAFTER CLEANING")
print(clean_df.shape)
print(clean_df.dtypes)