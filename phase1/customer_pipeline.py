import pandas as pd
import logging
from datetime import datetime

from customer_cleaner import CustomerCleaner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def load_data(filepath):
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} rows from {filepath}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise


def build_features(df):
    try:
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

        logger.info("Feature engineering completed")

        return df

    except Exception as e:
        logger.error(f"Feature engineering failed: {e}")
        raise


def save_outputs(clean_df, feature_df, output_dir="."):
    try:
        timestamp = datetime.now().strftime("%Y%m%d")

        clean_file = f"{output_dir}/cleaned_customer_{timestamp}.csv"
        feature_file = f"{output_dir}/customer_features_{timestamp}.csv"

        clean_df.to_csv(clean_file, index=False)
        feature_df.to_csv(feature_file, index=False)

        logger.info(f"Cleaned data saved to {clean_file}")
        logger.info(f"Feature data saved to {feature_file}")

    except Exception as e:
        logger.error(f"Saving failed: {e}")
        raise


def main():
    logger.info("Pipeline Started")

    try:
        raw_df = load_data("customer_churn.csv")

        cleaner = CustomerCleaner(raw_df)
        clean_df = cleaner.clean()

        feature_df = build_features(clean_df.copy())

        assert clean_df["monthlycharges"].isnull().sum() == 0, \
            "monthlycharges contains null values"

        assert set(clean_df["churn"].unique()).issubset({0, 1}), \
            "churn contains invalid values"

        save_outputs(clean_df, feature_df)

        logger.info("Pipeline Completed Successfully")

    except Exception as e:
        logger.error(f"Pipeline Failed: {e}")
        raise


if __name__ == "__main__":
    main()