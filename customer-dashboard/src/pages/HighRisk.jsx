import { useEffect, useState } from "react";
import { api } from "../api";

function HighRisk() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/customers/high-risk?limit=50")
      .then((result) => {
        setCustomers(result);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <p>Loading high-risk customers...</p>;
  }

  if (error) {
    return <p className="error">{error}</p>;
  }

  return (
    <div>
      <h2>High-Risk Customers</h2>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Customer ID</th>
              <th>Tenure</th>
              <th>Monthly Charges</th>
              <th>Contract</th>
              <th>Risk Reason</th>
            </tr>
          </thead>

          <tbody>
            {customers.map((customer) => (
              <tr key={customer.customer_id}>
                <td>{customer.customer_id}</td>
                <td>{customer.tenure}</td>
                <td>{customer.monthly_charges}</td>
                <td>{customer.contract_type}</td>
                <td>{customer.risk_reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default HighRisk;