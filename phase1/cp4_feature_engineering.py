import pandas as pd

from customer_cleaner import CustomerCleaner

df = pd.read_csv("customer_churn.csv")

cleaner = CustomerCleaner(df)
df = cleaner.clean()

df["tenure_bucket"] = pd.cut(
    df["tenure"],
    bins=[0, 12, 24, 48, 72],
    labels=["0-12", "13-24", "25-48", "49-72"],
    include_lowest=True
)

median_charge = df["monthlycharges"].median()

df["high_charge_flag"] = (
    df["monthlycharges"] > median_charge
).astype(int)

service_columns = [
    "onlinesecurity",
    "onlinebackup",
    "deviceprotection",
    "techsupport",
    "streamingtv",
    "streamingmovies"
]

df["service_count"] = df[service_columns].sum(axis=1)

df["is_long_term_customer"] = (
    df["tenure"] >= 24
).astype(int)

df["has_streaming_bundle"] = (
    (df["streamingtv"] == 1) &
    (df["streamingmovies"] == 1)
).astype(int)

df["auto_pay_flag"] = (
    df["paymentmethod"]
    .str.contains("automatic", case=False)
).astype(int)

print("=" * 60)
print("CORRELATION WITH CHURN")
print("=" * 60)

features = [
    "high_charge_flag",
    "service_count",
    "is_long_term_customer",
    "has_streaming_bundle",
    "auto_pay_flag"
]

print(df[features].corrwith(df["churn"]))

df.to_csv("customer_features.csv", index=False)

print("\ncustomer_features.csv saved successfully.")