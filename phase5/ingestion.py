import os
import csv
import shutil
import logging
import pandas as pd

from sqlalchemy import text
from database import engine


LANDING_DIR = "data/landing"
RAW_DIR = "data/raw"
REJECTED_DIR = "data/rejected"
LOG_DIR = "data/logs"


EXPECTED_COLS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn"
]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


def detect_files():
    files = []

    for filename in os.listdir(LANDING_DIR):
        if filename.lower().endswith(".csv"):
            files.append(
                os.path.join(LANDING_DIR, filename)
            )

    logger.info(
        "Detected %d CSV file(s)",
        len(files)
    )

    return files


def validate_schema(filepath):

    with open(
        filepath,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        header = next(csv.reader(f))

    is_valid = header == EXPECTED_COLS

    if is_valid:
        logger.info(
            "Schema validation passed: %s",
            os.path.basename(filepath)
        )
    else:
        logger.error(
            "Schema validation failed: %s",
            os.path.basename(filepath)
        )

    return is_valid, header


def load_to_staging(filepath, engine):

    df = pd.read_csv(filepath)

    df.to_sql(
        "stg_customer_raw",
        engine,
        if_exists="replace",
        index=False
    )

    row_count = len(df)

    logger.info(
        "Loaded %d rows into stg_customer_raw",
        row_count
    )

    return row_count


def log_ingestion(
    filename,
    status,
    rows,
    reason
):

    query = text("""
        INSERT INTO ingestion_log
        (
            file_name,
            rows_loaded,
            load_time,
            status,
            reason
        )
        VALUES
        (
            :file_name,
            :rows_loaded,
            NOW(),
            :status,
            :reason
        )
    """)

    with engine.begin() as connection:

        connection.execute(
            query,
            {
                "file_name": filename,
                "rows_loaded": rows,
                "status": status,
                "reason": reason
            }
        )

    logger.info(
        "Ingestion logged: %s - %s",
        filename,
        status
    )


def process_landing():

    files = detect_files()

    for filepath in files:

        filename = os.path.basename(filepath)

        try:

            logger.info(
                "Processing file: %s",
                filename
            )

            valid, header = validate_schema(
                filepath
            )

            if not valid:

                reason = (
                    f"Column mismatch. "
                    f"Expected {len(EXPECTED_COLS)} columns, "
                    f"received {len(header)} columns."
                )

                log_ingestion(
                    filename,
                    "REJECTED",
                    0,
                    reason
                )

                rejected_path = os.path.join(
                    REJECTED_DIR,
                    filename
                )

                shutil.move(
                    filepath,
                    rejected_path
                )

                logger.warning(
                    "Rejected file moved to: %s",
                    rejected_path
                )

                continue

            row_count = load_to_staging(
                filepath,
                engine
            )

            log_ingestion(
                filename,
                "LOADED",
                row_count,
                "Schema validation passed"
            )

            raw_path = os.path.join(
                RAW_DIR,
                filename
            )

            shutil.move(
                filepath,
                raw_path
            )

            logger.info(
                "Valid file moved to raw: %s",
                raw_path
            )

        except Exception as e:

            logger.exception(
                "Failed to process %s",
                filename
            )

            log_ingestion(
                filename,
                "REJECTED",
                0,
                str(e)
            )


if __name__ == "__main__":
    process_landing()