import { useState } from "react";
import { api } from "../api";

function Features() {
  const [customerId, setCustomerId] = useState("");
  const [features, setFeatures] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const getFeatures = async () => {
    if (!customerId.trim()) {
      setError("Enter a customer ID");
      return;
    }

    setLoading(true);
    setError("");
    setFeatures(null);

    try {
      const result = await api.get(
        `/customer/${customerId.trim()}/features`
      );

      setFeatures(result);
    } catch (err) {
      setError(err.message);
    }

    setLoading(false);
  };

  return (
    <div>
      <h2>Customer ML Features</h2>

      <div className="search-box">
        <input
          type="text"
          placeholder="Enter Customer ID"
          value={customerId}
          onChange={(e) => setCustomerId(e.target.value)}
        />

        <button onClick={getFeatures}>
          Get Features
        </button>
      </div>

      {loading && <p>Loading features...</p>}

      {error && <p className="error">{error}</p>}

      {features && (
        <div className="feature-grid">

          <div className="feature-card">
            <span>Service Count</span>
            <strong>{features.service_count}</strong>
          </div>

          <div className="feature-card">
            <span>Tenure Bucket</span>
            <strong>{features.tenure_bucket}</strong>
          </div>

          <div className="feature-card">
            <span>High Charge Flag</span>
            <strong>{features.high_charge_flag}</strong>
          </div>

          <div className="feature-card">
            <span>Long Term Customer</span>
            <strong>{features.is_long_term_customer}</strong>
          </div>

          <div className="feature-card">
            <span>Streaming Bundle</span>
            <strong>{features.has_streaming_bundle}</strong>
          </div>

          <div className="feature-card">
            <span>Auto Pay</span>
            <strong>{features.auto_pay_flag}</strong>
          </div>

          <div className="feature-card">
            <span>Monthly Charges</span>
            <strong>{features.monthly_charges}</strong>
          </div>

          <div className="feature-card">
            <span>Total Charges</span>
            <strong>{features.total_charges}</strong>
          </div>

        </div>
      )}
    </div>
  );
}

export default Features;