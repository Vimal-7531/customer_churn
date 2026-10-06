from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import text
from database import SessionLocal
from predict import predict_churn as model_predict_churn
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

API_KEY = os.getenv("API_KEY", "mysecretkey")


def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )


class CustomerResponse(BaseModel):
    customer_id: str
    tenure: int
    contract_type: str
    monthly_charges: float
    churn: int


class HighRiskCustomerResponse(BaseModel):
    customer_id: str
    tenure: int
    monthly_charges: float
    contract_type: str
    risk_reason: str


class CustomerFeaturesResponse(BaseModel):
    customer_id: str
    service_count: int
    tenure_bucket: str
    high_charge_flag: int
    is_long_term_customer: int
    has_streaming_bundle: int
    auto_pay_flag: int
    monthly_charges: float
    total_charges: float


class ChurnPredictionRequest(BaseModel):
    tenure: int = Field(..., ge=0, le=100)
    monthly_charges: float = Field(..., gt=0)
    contract_type: str
    service_count: int


class ErrorResponse(BaseModel):
    detail: str
    status_code: int


@app.get("/customer/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: str,
    x_api_key: str = Header(None)
):

    verify_api_key(x_api_key)

    logger.info(f"GET /customer/{customer_id}")

    db = None

    try:
        db = SessionLocal()

        query = text("""
            SELECT
                c.customer_id,
                a.tenure,
                ct.contract_name AS contract_type,
                a.monthly_charges,
                a.churn
            FROM customers c
            JOIN customer_account a
                ON c.customer_id = a.customer_id
            JOIN contracts ct
                ON a.contract_id = ct.contract_id
            WHERE c.customer_id = :customer_id
        """)

        result = db.execute(
            query,
            {"customer_id": customer_id}
        ).fetchone()

        if result is None:
            logger.info("404 Customer not found")
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        logger.info("200 OK")

        return {
            "customer_id": result.customer_id,
            "tenure": result.tenure,
            "contract_type": result.contract_type,
            "monthly_charges": float(result.monthly_charges),
            "churn": result.churn
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )

    finally:
        if db:
            db.close()


@app.get("/churn/summary")
def churn_summary(
    x_api_key: str = Header(None)
):

    verify_api_key(x_api_key)

    logger.info("GET /churn/summary")

    db = None

    try:
        db = SessionLocal()

        total = db.execute(text("""
            SELECT COUNT(*)
            FROM customer_account
        """)).scalar()

        churned = db.execute(text("""
            SELECT COUNT(*)
            FROM customer_account
            WHERE churn = 1
        """)).scalar()

        contract_summary = db.execute(text("""
            SELECT
                c.contract_name,
                ROUND(AVG(a.churn), 4) AS churn_rate
            FROM customer_account a
            JOIN contracts c
                ON a.contract_id = c.contract_id
            GROUP BY c.contract_name
        """)).fetchall()

        logger.info("200 OK")

        return {
            "total_customers": total,
            "total_churned": churned,
            "churn_rate": round(churned / total, 4),
            "by_contract": [
                {
                    "contract_type": row.contract_name,
                    "churn_rate": float(row.churn_rate)
                }
                for row in contract_summary
            ]
        }

    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )

    finally:
        if db:
            db.close()


@app.get(
    "/customers/high-risk",
    response_model=list[HighRiskCustomerResponse]
)
def get_high_risk_customers(
    limit: int = 50,
    min_tenure: int = 0,
    max_tenure: int = 100,
    x_api_key: str = Header(None)
):

    verify_api_key(x_api_key)

    logger.info(
        f"GET /customers/high-risk "
        f"limit={limit}, "
        f"min_tenure={min_tenure}, "
        f"max_tenure={max_tenure}"
    )

    db = None

    try:
        db = SessionLocal()

        query = text("""
            SELECT
                customer_id,
                tenure,
                monthly_charges,
                contract,
                risk_reason
            FROM v_high_risk_customers
            WHERE tenure BETWEEN :min_tenure AND :max_tenure
            LIMIT :limit
        """)

        result = db.execute(
            query,
            {
                "limit": limit,
                "min_tenure": min_tenure,
                "max_tenure": max_tenure
            }
        ).fetchall()

        logger.info("200 OK")

        return [
            {
                "customer_id": row.customer_id,
                "tenure": row.tenure,
                "monthly_charges": float(row.monthly_charges),
                "contract_type": row.contract,
                "risk_reason": row.risk_reason
            }
            for row in result
        ]

    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )

    finally:
        if db:
            db.close()


@app.get(
    "/customer/{customer_id}/features",
    response_model=CustomerFeaturesResponse
)
def get_customer_features(
    customer_id: str,
    x_api_key: str = Header(None)
):

    verify_api_key(x_api_key)

    logger.info(f"GET /customer/{customer_id}/features")

    db = None

    try:
        db = SessionLocal()

        query = text("""
            SELECT
                customer_id,
                service_count,
                tenure_bucket,
                high_charge_flag,
                is_long_term_customer,
                has_streaming_bundle,
                auto_pay_flag,
                monthly_charges,
                total_charges
            FROM customer_ml_features
            WHERE customer_id = :customer_id
        """)

        result = db.execute(
            query,
            {"customer_id": customer_id}
        ).fetchone()

        if result is None:
            logger.info("404 Customer not found")
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        logger.info("200 OK")

        return {
            "customer_id": result.customer_id,
            "service_count": result.service_count,
            "tenure_bucket": result.tenure_bucket,
            "high_charge_flag": result.high_charge_flag,
            "is_long_term_customer": result.is_long_term_customer,
            "has_streaming_bundle": result.has_streaming_bundle,
            "auto_pay_flag": result.auto_pay_flag,
            "monthly_charges": float(result.monthly_charges),
            "total_charges": float(result.total_charges)
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )

    finally:
        if db:
            db.close()

@app.post("/predict-churn")
def predict_churn(
    request: ChurnPredictionRequest,
    x_api_key: str = Header(None)
):

    verify_api_key(x_api_key)

    logger.info(
        f"POST /predict-churn "
        f"tenure={request.tenure}, "
        f"contract_type={request.contract_type}, "
        f"service_count={request.service_count}"
    )

    result = model_predict_churn(
        tenure=request.tenure,
        monthly_charges=request.monthly_charges,
        contract_type=request.contract_type,
        service_count=request.service_count
    )

    logger.info("200 OK")

    return result


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": str(exc.detail),
            "status_code": exc.status_code
        }
    )


@app.exception_handler(404)
async def not_found_handler(
    request: Request,
    exc
):

    return JSONResponse(
        status_code=404,
        content={
            "detail": "Resource not found",
            "status_code": 404
        }
    )