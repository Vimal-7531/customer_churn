import logging
import pandas as pd

from sqlalchemy import text
from database import engine
from customer_cleaner import CustomerCleaner


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


def clean_staging(engine):

    logger.info("Reading data from stg_customer_raw")

    df = pd.read_sql(
        "SELECT * FROM stg_customer_raw",
        engine
    )

    staging_count = len(df)

    logger.info(
        "Rows read from staging: %d",
        staging_count
    )
    cleaner = CustomerCleaner(df)

    cleaned_df = cleaner.clean()

    print("\nCLEANED COLUMNS:")
    print(cleaned_df.columns.tolist())

    cleaned_df.to_sql(
        "cleaned_customers",
        engine,
        if_exists="replace",
        index=False
    )

    cleaned_count = len(cleaned_df)

    logger.info(
        "Rows written to cleaned_customers: %d",
        cleaned_count
    )

    assert cleaned_count == staging_count, (
        "FAIL: Row count changed during cleaning"
    )

    print(
        f"PASS: Row count check - "
        f"staging={staging_count}, "
        f"cleaned={cleaned_count}"
    )

    return cleaned_df


def quality_checks(df):

    print("\nDATA QUALITY REPORT")
    print("-------------------")

    null_customer_id = df["customer_id"].isnull().sum()

    if null_customer_id == 0:
        print("PASS: customer_id has no NULL values")
    else:
        print(
            f"FAIL: customer_id has "
            f"{null_customer_id} NULL values"
        )

    null_monthly_charges = df["monthly_charges"].isnull().sum()

    if null_monthly_charges == 0:
        print("PASS: monthly_charges has no NULL values")
    else:
        print(
            f"FAIL: monthly_charges has "
            f"{null_monthly_charges} NULL values"
        )

    invalid_churn = df[
        ~df["churn"].isin([0, 1])
    ]

    invalid_churn_count = len(invalid_churn)

    if invalid_churn_count == 0:
        print("PASS: churn contains only 0 and 1")
    else:
        print(
            f"FAIL: churn contains "
            f"{invalid_churn_count} invalid values"
        )

    assert null_customer_id == 0
    assert null_monthly_charges == 0
    assert invalid_churn_count == 0

def build_curated_tables(cleaned_df, engine):

    logger.info("Building curated tables")

    with engine.begin() as conn:

        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        conn.execute(text("DROP TABLE IF EXISTS customer_account"))
        conn.execute(text("DROP TABLE IF EXISTS customers"))
        conn.execute(text("DROP TABLE IF EXISTS contracts"))
        conn.execute(text("DROP TABLE IF EXISTS payments"))

        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

    contracts = (
        cleaned_df[["contract"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    contracts.insert(
        0,
        "contract_id",
        range(1, len(contracts) + 1)
    )

    contracts.rename(
        columns={
            "contract": "contract_name"
        },
        inplace=True
    )

    contracts.to_sql(
        "contracts",
        engine,
        if_exists="replace",
        index=False
    )

    logger.info(
        "Contracts table populated: %d rows",
        len(contracts)
    )

    payments = (
        cleaned_df[["payment_method"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    payments.insert(
        0,
        "payment_id",
        range(1, len(payments) + 1)
    )

    payments.to_sql(
        "payments",
        engine,
        if_exists="replace",
        index=False
    )

    logger.info(
        "Payments table populated: %d rows",
        len(payments)
    )

    customers = cleaned_df[
        [
            "customer_id",
            "gender",
            "senior_citizen",
            "partner",
            "dependents"
        ]
    ].copy()

    customers.to_sql(
        "customers",
        engine,
        if_exists="replace",
        index=False
    )

    logger.info(
        "Customers table populated: %d rows",
        len(customers)
    )

    accounts = cleaned_df[
        [
            "customer_id",
            "tenure",
            "monthly_charges",
            "total_charges",
            "churn",
            "contract",
            "payment_method"
        ]
    ].copy()

    accounts = accounts.merge(
        contracts,
        left_on="contract",
        right_on="contract_name",
        how="left"
    )

    accounts = accounts.merge(
        payments,
        on="payment_method",
        how="left"
    )

    accounts = accounts[
        [
            "customer_id",
            "contract_id",
            "payment_id",
            "tenure",
            "monthly_charges",
            "total_charges",
            "churn"
        ]
    ]

    accounts.insert(
        0,
        "account_id",
        range(1, len(accounts) + 1)
    )

    accounts.to_sql(
        "customer_account",
        engine,
        if_exists="replace",
        index=False
    )

    logger.info(
        "Customer account table populated: %d rows",
        len(accounts)
    )

    logger.info("All curated tables built successfully")

def main():

    logger.info("DE3 cleaning stage started")

    cleaned_df = clean_staging(engine)

    quality_checks(cleaned_df)

    build_curated_tables(
    cleaned_df,
    engine
    )

    logger.info("DE3 cleaning stage completed")


if __name__ == "__main__":
    main()