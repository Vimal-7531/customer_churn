import pandas as pd
import json
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


def check_null_rate(df, col, threshold):
    null_rate = df[col].isnull().mean() * 100

    passed = null_rate <= threshold

    return {
        "check": f"Null rate - {col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": round(null_rate, 2),
        "threshold": threshold,
        "severity": "CRITICAL"
    }


def check_value_range(df, col, minimum, maximum):
    invalid_count = (
        (df[col] < minimum) |
        (df[col] > maximum)
    ).sum()

    passed = invalid_count == 0

    return {
        "check": f"Value range - {col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": int(invalid_count),
        "threshold": f"{minimum} to {maximum}",
        "severity": "CRITICAL"
    }


def check_allowed_values(df, col, allowed_set):
    invalid_count = (~df[col].isin(allowed_set)).sum()

    passed = invalid_count == 0

    return {
        "check": f"Allowed values - {col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": int(invalid_count),
        "threshold": list(allowed_set),
        "severity": "CRITICAL"
    }


def check_row_count(df, expected_min):
    row_count = len(df)

    passed = row_count >= expected_min

    return {
        "check": "Row count",
        "status": "PASS" if passed else "FAIL",
        "value_found": row_count,
        "threshold": expected_min,
        "severity": "CRITICAL"
    }


def check_no_duplicates(df, key_col):
    duplicate_count = df[key_col].duplicated().sum()

    passed = duplicate_count == 0

    return {
        "check": f"Duplicate check - {key_col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": int(duplicate_count),
        "threshold": 0,
        "severity": "CRITICAL"
    }


def check_churn_distribution(df):
    invalid_count = (~df["churn"].isin([0, 1])).sum()

    passed = invalid_count == 0

    return {
        "check": "Churn distribution",
        "status": "PASS" if passed else "FAIL",
        "value_found": int(invalid_count),
        "threshold": "Only 0 and 1",
        "severity": "CRITICAL"
    }


def run_quality_checks(df):

    results = []

    results.append(
        check_null_rate(df, "monthly_charges", 0)
    )

    results.append(
        check_null_rate(df, "tenure", 0)
    )

    results.append(
        check_value_range(df, "tenure", 0, 100)
    )

    results.append(
        check_value_range(df, "monthly_charges", 0.01, float("inf"))
    )

    results.append(
        check_allowed_values(
            df,
            "contract",
            {
                "Month-to-month",
                "One year",
                "Two year"
            }
        )
    )

    results.append(
        check_row_count(df, 7000)
    )

    results.append(
        check_no_duplicates(df, "customer_id")
    )

    results.append(
        check_churn_distribution(df)
    )

    return results


def save_quality_report(results):

    with open("quality_report.json", "w") as file:
        json.dump(results, file, indent=4)

    logger.info("quality_report.json created")


def validate_results(results):

    critical_failures = [
        result
        for result in results
        if result["status"] == "FAIL"
        and result["severity"] == "CRITICAL"
    ]

    for result in results:

        if result["status"] == "PASS":
            logger.info(
                "PASS: %s",
                result["check"]
            )

        else:
            logger.error(
                "FAIL: %s",
                result["check"]
            )

    if critical_failures:

        raise Exception(
            f"CRITICAL DATA QUALITY FAILURE: "
            f"{len(critical_failures)} check(s) failed"
        )


def main():

    logger.info("DE7 data quality checks started")

    df = pd.read_csv("data/raw/customer_churn.csv")

    df.columns = [
        "customer_id",
        "gender",
        "senior_citizen",
        "partner",
        "dependents",
        "tenure",
        "phone_service",
        "multiple_lines",
        "internet_service",
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
        "contract",
        "paperless_billing",
        "payment_method",
        "monthly_charges",
        "total_charges",
        "churn"
    ]

    df["partner"] = df["partner"].map({
        "Yes": 1,
        "No": 0
    })

    df["dependents"] = df["dependents"].map({
        "Yes": 1,
        "No": 0
    })

    df["phone_service"] = df["phone_service"].map({
        "Yes": 1,
        "No": 0
    })

    df["paperless_billing"] = df["paperless_billing"].map({
        "Yes": 1,
        "No": 0
    })

    df["churn"] = df["churn"].map({
        "Yes": 1,
        "No": 0
    })

    df["monthly_charges"] = pd.to_numeric(
        df["monthly_charges"],
        errors="coerce"
    )

    df["tenure"] = pd.to_numeric(
        df["tenure"],
        errors="coerce"
    )

    results = run_quality_checks(df)

    save_quality_report(results)

    validate_results(results)

    logger.info("All critical quality checks passed")
    logger.info("DE7 completed successfully")


if __name__ == "__main__":
    main()