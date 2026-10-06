import { useState } from "react";
import { api } from "../api";

function Prediction() {
  const [form, setForm] = useState({
    tenure: "",
    monthly_charges: "",
    contract_type: "Month-to-month",
    service_count: ""
  });

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const predict = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const result = await api.post("/predict-churn", {
        tenure: Number(form.tenure),
        monthly_charges: Number(form.monthly_charges),
        contract_type: form.contract_type,
        service_count: Number(form.service_count)
      });

      setResult(result);
    } catch (err) {
      setError(err.message);
    }

    setLoading(false);
  };

  return (
    <div>
      <h2>Churn Prediction</h2>

      <form className="prediction-form" onSubmit={predict}>

        <label>
          Tenure
          <input
            type="number"
            name="tenure"
            value={form.tenure}
            onChange={handleChange}
            min="0"
            max="100"
            required
          />
        </label>

        <label>
          Monthly Charges
          <input
            type="number"
            name="monthly_charges"
            value={form.monthly_charges}
            onChange={handleChange}
            min="0.01"
            step="0.01"
            required
          />
        </label>

        <label>
          Contract Type
          <select
            name="contract_type"
            value={form.contract_type}
            onChange={handleChange}
          >
            <option value="Month-to-month">
              Month-to-month
            </option>

            <option value="One year">
              One year
            </option>

            <option value="Two year">
              Two year
            </option>
          </select>
        </label>

        <label>
          Service Count
          <input
            type="number"
            name="service_count"
            value={form.service_count}
            onChange={handleChange}
            min="0"
            required
          />
        </label>

        <button type="submit">
          Predict Churn
        </button>

      </form>

      {loading && <p>Predicting...</p>}

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="prediction-result">

          <h3>Prediction Result</h3>

          <p>
            <strong>Risk Score:</strong>{" "}
            {(result.risk_score * 100).toFixed(0)}%
          </p>

          <p>
            <strong>Prediction:</strong>{" "}
            {result.prediction}
          </p>

          <p>
            <strong>Note:</strong>{" "}
            {result.note}
          </p>

        </div>
      )}
    </div>
  );
}

export default Prediction;