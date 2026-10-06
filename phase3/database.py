from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:root@localhost/customer_churn"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)