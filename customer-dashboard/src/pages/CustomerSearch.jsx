import { useState } from "react";
import { api } from "../api";

function CustomerSearch() {
  const [customerId, setCustomerId] = useState("");
  const [customer, setCustomer] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const searchCustomer = async () => {
    if (!customerId.trim()) {
      setError("Enter a customer ID");
      return;
    }

    setLoading(true);
    setError("");
    setCustomer(null);

    try {
      const result = await api.get(
        `/customer/${customerId.trim()}`
      );

      setCustomer(result);
    } catch (err) {
      setError(err.message);
    }

    setLoading(false);
  };

  return (
    <div>
      <h2>Customer Search</h2>

      <div className="search-box">
        <input
          type="text"
          placeholder="Enter Customer ID"
          value={customerId}
          onChange={(e) => setCustomerId(e.target.value)}
        />

        <button onClick={searchCustomer}>
          Search
        </button>
      </div>

      {loading && <p>Searching...</p>}

      {error && <p className="error">{error}</p>}

      {customer && (
        <div className="card customer-details">
          <h3>Customer Details</h3>

          <p>
            <strong>Customer ID:</strong>{" "}
            {customer.customer_id}
          </p>

          <p>
            <strong>Tenure:</strong> {customer.tenure}
          </p>

          <p>
            <strong>Contract:</strong>{" "}
            {customer.contract_type}
          </p>

          <p>
            <strong>Monthly Charges:</strong>{" "}
            {customer.monthly_charges}
          </p>

          <p>
            <strong>Churn:</strong>{" "}
            {customer.churn === 1 ? "Yes" : "No"}
          </p>
        </div>
      )}
    </div>
  );
}

export default CustomerSearch;