import { useEffect, useState } from "react";
import { api } from "../api";

function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/churn/summary")
      .then((result) => {
        setData(result);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <p>Loading dashboard...</p>;
  }

  if (error) {
    return <p className="error">{error}</p>;
  }

  return (
    <div>
      <h2>Dashboard</h2>

      <div className="stats">

        <div className="stat-card">
          <h3>Total Customers</h3>
          <p>{data.total_customers}</p>
        </div>

        <div className="stat-card">
          <h3>Total Churned</h3>
          <p>{data.total_churned}</p>
        </div>

        <div className="stat-card">
          <h3>Churn Rate</h3>
          <p>{(data.churn_rate * 100).toFixed(2)}%</p>
        </div>

      </div>

      <div className="card">
        <h3>Churn by Contract</h3>

        {data.by_contract.map((item) => (
          <div className="contract-row" key={item.contract_type}>
            <span>{item.contract_type}</span>
            <strong>
              {(item.churn_rate * 100).toFixed(2)}%
            </strong>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;