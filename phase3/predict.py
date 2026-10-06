import pandas as pd
import joblib


model = joblib.load(
    "../phase6/models/api_churn.pkl"
)

FEATURE_COLUMNS = joblib.load(
    "../phase6/models/api_feature_columns.pkl"
)


def preprocess_input(
    tenure,
    monthly_charges,
    contract_type,
    service_count
):

    input_data = {
        "tenure": tenure,
        "monthly_charges": monthly_charges,
        "service_count": service_count,
        "contract": contract_type
    }

    df = pd.DataFrame([input_data])

    df = pd.get_dummies(
        df,
        columns=["contract"],
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

    probability = model.predict_proba(
        input_df
    )[0][1]

    if probability >= 0.5:
        prediction = "Likely to churn"
    else:
        prediction = "Unlikely to churn"

    confidence = max(
        probability,
        1 - probability
    )

    return {
        "risk_score": round(float(probability), 4),
        "prediction": prediction,
        "confidence": round(float(confidence), 4)
    }