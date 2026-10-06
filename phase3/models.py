from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DECIMAL

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(20), primary_key=True)
    gender = Column(String(10))
    senior_citizen = Column(Integer)
    partner = Column(Integer)
    dependents = Column(Integer)


class Contract(Base):
    __tablename__ = "contracts"

    contract_id = Column(Integer, primary_key=True)
    contract_name = Column(String(30))


class CustomerAccount(Base):
    __tablename__ = "customer_account"

    account_id = Column(Integer, primary_key=True)
    customer_id = Column(String(20))
    contract_id = Column(Integer)
    payment_id = Column(Integer)
    tenure = Column(Integer)
    monthly_charges = Column(DECIMAL(10,2))
    total_charges = Column(DECIMAL(10,2))
    churn = Column(Integer)