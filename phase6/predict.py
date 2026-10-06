import pandas as pd
import joblib
from sqlalchemy import create_engine


DATABASE_URL = "mysql+pymysql://root:root@localhost/customer_churn"

engine = create_engine(DATABASE_URL)

model = joblib.load("models/tree_churn.pkl")

print("Decision Tree model loaded")


def get_training_columns():

    query = """
    SELECT *
    FROM customer_ml_features
    """

    df = pd.read_sql(query, engine)

    X = df.drop(
        columns=["customer_id", "churn"]
    )

    categorical_columns = X.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    X = pd.get_dummies(
        X,
        columns=categorical_columns,
        drop_first=False
    )

    X = X.astype(float)

    return X.columns.tolist()


FEATURE_COLUMNS = get_training_columns()


def preprocess_input(
    tenure,
    monthly_charges,
    contract_type,
    service_count
):

    input_data = {
        "tenure": tenure,
        "monthly_charges": monthly_charges,
        "total_charges": monthly_charges * tenure,
        "service_count": service_count,
        "high_charge_flag": 0,
        "is_long_term_customer": 1 if tenure >= 24 else 0,
        "has_streaming_bundle": 0,
        "auto_pay_flag": 0
    }

    categorical_defaults = {
        "gender": "Male",
        "partner": 0,
        "dependents": 0,
        "phone_service": "Yes",
        "multiple_lines": "No",
        "internet_service": "DSL",
        "online_security": "No",
        "online_backup": "No",
        "device_protection": "No",
        "tech_support": "No",
        "streaming_tv": "No",
        "streaming_movies": "No",
        "paperless_billing": "Yes",
        "payment_method": "Electronic check",
        "tenure_bucket": "0-12"
    }

    input_data.update(categorical_defaults)

    input_data["contract"] = contract_type

    df = pd.DataFrame([input_data])

    categorical_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    df = pd.get_dummies(
        df,
        columns=categorical_columns,
        drop_first=False
    )

    df = df.reindex(
        columns=FEATURE_COLUMNS,
        fill_value=0
    )

    df = df.astype(float)

    return df


def predict_churn(
    tenure,
    monthly_charges,
    contract_type,
    service_count
):

    input_df = preprocess_input(
        tenure=tenure,
        monthly_charges=monthly_charges,
        contract_type=contract_type,
        service_count=service_count
    )

    prediction = model.predict(input_df)[0]

    probability = model.predict_proba(
        input_df
    )[0][1]

    if prediction == 1:
        result = "Likely to churn"
    else:
        result = "Unlikely to churn"

    return {
        "risk_score": round(float(probability), 4),
        "prediction": result,
        "confidence": round(
            float(max(model.predict_proba(input_df)[0])),
            4
        )
    }