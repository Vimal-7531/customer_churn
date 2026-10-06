import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class CustomerCleaner:

    def __init__(self, df):
        self.df = df.copy()

    def standardize_column_names(self):
        logger.info("Standardizing column names...")

        self.df.columns = (
            self.df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        return self

    def fix_total_charges(self):
        logger.info("Fixing total_charges column...")

        try:
            blanks = (self.df["totalcharges"] == " ").sum()

            self.df["totalcharges"] = (
                self.df["totalcharges"]
                .replace(" ", pd.NA)
            )

            self.df["totalcharges"] = pd.to_numeric(
                self.df["totalcharges"],
                errors="coerce"
            )

            logger.info(f"{blanks} blank values converted to NaN")

        except Exception as e:
            logger.error(f"Error while fixing total_charges: {e}")

        return self

    def normalize_binary_columns(self):
        logger.info("Normalizing binary columns...")

        binary_columns = [
            "partner",
            "dependents",
            "phoneservice",
            "paperlessbilling",
            "churn",
            "onlinesecurity",
            "onlinebackup",
            "deviceprotection",
            "techsupport",
            "streamingtv",
            "streamingmovies"
        ]

        mapping = {
            "Yes": 1,
            "No": 0,
            "No internet service": 0
        }

        for col in binary_columns:
            self.df[col] = self.df[col].map(mapping)
        return self

    def handle_nulls(self):
        logger.info("Handling missing values...")

        nulls = self.df["totalcharges"].isna().sum()

        self.df["totalcharges"] = self.df["totalcharges"].fillna(
            self.df["monthlycharges"]
        )

        logger.info(f"{nulls} null values filled")

        return self

    def clean(self):
        logger.info("Starting cleaning process...")

        self.standardize_column_names()
        self.fix_total_charges()
        self.normalize_binary_columns()
        self.handle_nulls()

        logger.info("Cleaning completed successfully.")

        return self.df

