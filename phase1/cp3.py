import pandas as pd
from customer_cleaner import CustomerCleaner

df = pd.read_csv("customer_churn.csv")

cleaner = CustomerCleaner(df)
df = cleaner.clean()

print("=" * 60)
print("CHURN RATE BY CONTRACT")
print("=" * 60)

contract_churn = (
    df.groupby("contract")["churn"]
    .mean()
    .sort_values(ascending=False)
    * 100
)

print(contract_churn.round(2))

print("\n" + "=" * 60)
print("CHURN RATE BY INTERNET SERVICE")
print("=" * 60)

internet_churn = (
    df.groupby("internetservice")["churn"]
    .mean()
    .sort_values(ascending=False)
    * 100
)

print(internet_churn.round(2))

print("\n" + "=" * 60)
print("CHURN RATE BY PAYMENT METHOD")
print("=" * 60)

payment_churn = (
    df.groupby("paymentmethod")["churn"]
    .mean()
    .sort_values(ascending=False)
    * 100
)

print(payment_churn.round(2))

print("\n" + "=" * 60)
print("CHURN RATE BY TENURE BUCKET")
print("=" * 60)

df["tenure_bucket"] = pd.cut(
    df["tenure"],
    bins=[0, 12, 24, 48, 72],
    labels=["0-12", "13-24", "25-48", "49-72"],
    include_lowest=True
)

tenure_churn = (
    df.groupby("tenure_bucket")["churn"]
    .mean()
    .sort_values(ascending=False)
    * 100
)

print(tenure_churn.round(2))

print("\n" + "=" * 60)
print("AVERAGE MONTHLY CHARGES")
print("=" * 60)

monthly_charges = (
    df.groupby("churn")["monthlycharges"]
    .mean()
)

print(monthly_charges.round(2))

print("\n" + "=" * 60)
print("CONTRACT + INTERNET SERVICE")
print("=" * 60)

contract_internet = (
    df.groupby(["contract", "internetservice"])["churn"]
    .mean()
    .sort_values(ascending=False)
    * 100
)

print(contract_internet.round(2))

print("\n" + "=" * 60)
print("BUSINESS SUMMARY")
print("=" * 60)

print("1. Customers with month-to-month contracts have the highest churn rate, especially those using fiber optic internet.")
print("2. Customers paying through electronic check and those with shorter tenure are more likely to leave the service.")
print("3. The retention team should prioritize these high-risk customer segments with targeted offers and proactive support to reduce churn.")