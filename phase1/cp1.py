import pandas as pd

df = pd.read_csv("customer_churn.csv")

print("=" * 60)
print("DATASET SHAPE")
print("=" * 60)
print(df.shape)

print("\n" + "=" * 60)
print("COLUMN NAMES")
print("=" * 60)
print(df.columns.tolist())

print("\n" + "=" * 60)
print("DATA TYPES")
print("=" * 60)
print(df.dtypes)

print("\n" + "=" * 60)
print("NULL VALUES")
print("=" * 60)

null_counts = df.isnull().sum()
null_percentage = (null_counts / len(df)) * 100

null_table = pd.DataFrame({
    "Null Count": null_counts,
    "Null Percentage": null_percentage.round(2)
})

print(null_table)

categorical_columns = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "InternetService",
    "Contract",
    "PaymentMethod",
    "Churn"
]

for column in categorical_columns:
    print("\n" + "=" * 60)
    print(f"{column}")
    print("=" * 60)

    print("\nUnique Values:")
    print(df[column].unique())

    print("\nValue Counts:")
    print(df[column].value_counts())

print("\n" + "=" * 60)
print("CHURN DISTRIBUTION")
print("=" * 60)

churn_counts = df["Churn"].value_counts()
print(churn_counts)

churn_rate = df["Churn"].value_counts(normalize=True) * 100

print("\nChurn Percentage")
print(churn_rate.round(2))

print("\n" + "=" * 60)
print("TOTAL CHARGES ANALYSIS")
print("=" * 60)

print("Original Data Type:")
print(df["TotalCharges"].dtype)

total_charges_numeric = pd.to_numeric(
    df["TotalCharges"],
    errors="coerce"
)

print("\nNaN Values After Conversion:")
print(total_charges_numeric.isna().sum())

print("\n" + "=" * 60)
print("NUMERICAL SUMMARY")
print("=" * 60)

print("\nTenure")
print("Minimum :", df["tenure"].min())
print("Maximum :", df["tenure"].max())
print("Mean    :", df["tenure"].mean())

print("\nMonthlyCharges")
print("Minimum :", df["MonthlyCharges"].min())
print("Maximum :", df["MonthlyCharges"].max())
print("Mean    :", df["MonthlyCharges"].mean())

print("\nTotalCharges")

print("Minimum :", total_charges_numeric.min())
print("Maximum :", total_charges_numeric.max())
print("Mean    :", total_charges_numeric.mean())

print("\n" + "=" * 60)
print("PROFILING SUMMARY")
print("=" * 60)

summary = [
    "1. Dataset contains customer information with demographic, service, billing and churn details.",
    "2. customerID is a unique identifier and should not be used as a machine learning feature.",
    "3. TotalCharges is stored as an object because some rows contain blank spaces that become NaN after numeric conversion.",
    "4. The dataset is imbalanced, with approximately 73% non-churned customers and 27% churned customers.",
    "5. Data quality issues such as missing or improperly formatted values should be handled before transformation or modeling."
]

for point in summary:
    print(point)