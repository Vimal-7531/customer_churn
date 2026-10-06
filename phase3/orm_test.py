from database import SessionLocal
from models import Customer

session = SessionLocal()

customer = session.query(Customer).filter_by(customer_id="7590-VHVEG").first()

if customer:
    print("Customer ID :", customer.customer_id)
    print("Gender      :", customer.gender)
    print("Partner     :", customer.partner)
    print("Dependents  :", customer.dependents)
else:
    print("Customer not found")

session.close()