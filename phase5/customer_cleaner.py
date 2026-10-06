import logging
import pandas as pd


logger = logging.getLogger(__name__)


class CustomerCleaner:

    def __init__(self, df):
        self.df = df.copy()

    def standardize_column_names(self):
        rename_map = {
            "customerID": "customer_id",
            "SeniorCitizen": "senior_citizen",
            "MonthlyCharges": "monthly_charges",
            "TotalCharges": "total_charges",
            "PhoneService": "phone_service",
            "MultipleLines": "multiple_lines",
            "InternetService": "internet_service",
            "OnlineSecurity": "online_security",
            "OnlineBackup": "online_backup",
            "DeviceProtection": "device_protection",
            "TechSupport": "tech_support",
            "StreamingTV": "streaming_tv",
            "StreamingMovies": "streaming_movies",
            "PaperlessBilling": "paperless_billing",
            "PaymentMethod": "payment_method"
        }

        self.df.rename(
            columns=rename_map,
            inplace=True
        )

        self.df.columns = [
            column.lower()
            for column in self.df.columns
        ]

        logger.info("Column names standardized")

        return self

    def fix_total_charges(self):

        try:

            logger.info(
                "Fixing total_charges column..."
            )

            self.df["total_charges"] = (
                self.df["total_charges"]
                .replace(r"^\s*$", pd.NA, regex=True)
            )

            self.df["total_charges"] = pd.to_numeric(
                self.df["total_charges"],
                errors="coerce"
            )

            affected_rows = (
                self.df["total_charges"]
                .isna()
                .sum()
            )

            logger.info(
                "total_charges conversion completed. "
                "NULL values: %d",
                affected_rows
            )

        except Exception as e:

            logger.error(
                "Error while fixing total_charges: %s",
                e
            )

            raise

        return self

    def normalize_binary_columns(self):

        logger.info(
            "Normalizing binary columns..."
        )

        binary_columns = [
            "partner",
            "dependents",
            "phone_service",
            "paperless_billing",
            "churn"
        ]

        mapping = {
            "Yes": 1,
            "No": 0
        }

        for column in binary_columns:

            self.df[column] = (
                self.df[column]
                .map(mapping)
            )

        logger.info(
            "Binary columns normalized"
        )

        return self

    def handle_nulls(self):

        logger.info(
            "Handling NULL values..."
        )

        null_count = (
            self.df["total_charges"]
            .isna()
            .sum()
        )

        self.df["total_charges"] = (
            self.df["total_charges"]
            .fillna(self.df["monthly_charges"])
        )

        logger.info(
            "Filled %d total_charges NULL values",
            null_count
        )

        return self

    def clean(self):

        logger.info(
            "Starting cleaning process..."
        )

        self.standardize_column_names()
        self.fix_total_charges()
        self.normalize_binary_columns()
        self.handle_nulls()

        logger.info(
            "Cleaning process completed"
        )

        return self.df