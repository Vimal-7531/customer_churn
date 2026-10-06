import logging
import pandas as pd
from sqlalchemy import create_engine, text


DATABASE_URL = "mysql+pymysql://root:root@localhost/customer_churn"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


def build_features(engine):

    logger.info("DE4 feature pipeline started")

    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    logger.info(
        "Rows read from cleaned_customers: %d",
        len(df)
    )

    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=["0-12", "13-24", "25-48", "49-72"],
        include_lowest=True
    )

    median_monthly_charges = df["monthly_charges"].median()

    df["high_charge_flag"] = (
        df["monthly_charges"] > median_monthly_charges
    ).astype(int)

    service_columns = [
    "phone_service",
    "multiple_lines",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support"
    ]

    df["service_count"] = (
        df[service_columns]
        .apply(
            lambda row: sum(
                str(value).strip().lower() == "yes"
                for value in row
            ),
            axis=1
        )
    )

    df["is_long_term_customer"] = (
        df["tenure"] >= 24
    ).astype(int)

    df["has_streaming_bundle"] = (
        (
            (df["streaming_tv"] == 1) &
            (df["streaming_movies"] == 1)
        )
    ).astype(int)

    df["auto_pay_flag"] = (
        df["payment_method"]
        .str.contains(
            "automatic",
            case=False,
            na=False
        )
    ).astype(int)

    feature_columns = [
        "tenure_bucket",
        "high_charge_flag",
        "service_count",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag"
    ]

    logger.info(
        "Checking feature columns"
    )

    for column in feature_columns:

        if column not in df.columns:
            raise ValueError(
                f"Missing feature column: {column}"
            )

        null_count = df[column].isnull().sum()

        if null_count > 0:
            raise ValueError(
                f"{column} contains {null_count} NULL values"
            )

        print(
            f"PASS: {column} exists and has no NULL values"
        )

    df.to_sql(
        "customer_ml_features",
        engine,
        if_exists="replace",
        index=False
    )

    logger.info(
        "customer_ml_features table populated: %d rows",
        len(df)
    )

    feature_count = pd.read_sql(
        "SELECT COUNT(*) AS count FROM customer_ml_features",
        engine
    ).iloc[0]["count"]

    cleaned_count = pd.read_sql(
        "SELECT COUNT(*) AS count FROM cleaned_customers",
        engine
    ).iloc[0]["count"]

    print()
    print("ROW COUNT VALIDATION")
    print("--------------------")

    if feature_count == cleaned_count:
        print(
            f"PASS: cleaned_customers={cleaned_count}, "
            f"customer_ml_features={feature_count}"
        )
    else:
        raise ValueError(
            f"Row count mismatch: "
            f"cleaned={cleaned_count}, "
            f"features={feature_count}"
        )

    print()
    print("FEATURE SCHEMA")
    print("--------------")

    for column in feature_columns:
        print(
            f"PASS: {column}"
        )

    logger.info(
        "DE4 feature pipeline completed successfully"
    )


if __name__ == "__main__":

    engine = create_engine(DATABASE_URL)

    build_features(engine)