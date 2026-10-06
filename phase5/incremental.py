import pandas as pd
from sqlalchemy import text
from database import engine
from datetime import datetime


def process_incremental(filepath):

    df = pd.read_csv(filepath)

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

    df["partner"] = df["partner"].map({"Yes": 1, "No": 0})
    df["dependents"] = df["dependents"].map({"Yes": 1, "No": 0})
    df["phone_service"] = df["phone_service"].map({"Yes": 1, "No": 0})
    df["paperless_billing"] = df["paperless_billing"].map({"Yes": 1, "No": 0})
    df["churn"] = df["churn"].map({"Yes": 1, "No": 0})

    df["total_charges"] = (
        df["total_charges"]
        .replace(" ", "")
        .replace("", None)
    )

    df["total_charges"] = pd.to_numeric(
        df["total_charges"],
        errors="coerce"
    )

    inserted = 0
    updated = 0
    unchanged = 0

    with engine.begin() as conn:

        for _, row in df.iterrows():

            existing = conn.execute(
                text("""
                    SELECT
                        customer_id,
                        gender,
                        senior_citizen,
                        partner,
                        dependents
                    FROM customers
                    WHERE customer_id = :customer_id
                """),
                {
                    "customer_id": row["customer_id"]
                }
            ).fetchone()

            if existing is None:

                conn.execute(
                    text("""
                        INSERT INTO customers (
                            customer_id,
                            gender,
                            senior_citizen,
                            partner,
                            dependents
                        )
                        VALUES (
                            :customer_id,
                            :gender,
                            :senior_citizen,
                            :partner,
                            :dependents
                        )
                    """),
                    {
                        "customer_id": row["customer_id"],
                        "gender": row["gender"],
                        "senior_citizen": row["senior_citizen"],
                        "partner": row["partner"],
                        "dependents": row["dependents"]
                    }
                )

                inserted += 1

            else:

                changed = (
                    existing.gender != row["gender"]
                    or existing.senior_citizen != row["senior_citizen"]
                    or existing.partner != row["partner"]
                    or existing.dependents != row["dependents"]
                )

                if changed:

                    conn.execute(
                        text("""
                            UPDATE customers
                            SET
                                gender = :gender,
                                senior_citizen = :senior_citizen,
                                partner = :partner,
                                dependents = :dependents
                            WHERE customer_id = :customer_id
                        """),
                        {
                            "customer_id": row["customer_id"],
                            "gender": row["gender"],
                            "senior_citizen": row["senior_citizen"],
                            "partner": row["partner"],
                            "dependents": row["dependents"]
                        }
                    )

                    updated += 1

                else:
                    unchanged += 1

        conn.execute(
            text("""
                INSERT INTO ingestion_log
                (
                    file_name,
                    rows_loaded,
                    load_time,
                    status
                )
                VALUES
                (
                    :file_name,
                    :rows_loaded,
                    :load_time,
                    :status
                )
            """),
            {
                "file_name": filepath,
                "rows_loaded": inserted + updated,
                "load_time": datetime.now(),
                "status": "INCREMENTAL"
            }
        )

    print("INCREMENTAL PROCESSING COMPLETE")
    print("------------------------------")
    print("Rows inserted  :", inserted)
    print("Rows updated   :", updated)
    print("Rows unchanged :", unchanged)


if __name__ == "__main__":
    process_incremental("data/raw/customer_churn_copy.csv")