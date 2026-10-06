import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import CustomerSearch from "./pages/CustomerSearch";
import HighRisk from "./pages/HighRisk";
import Features from "./pages/Features";
import Prediction from "./pages/Prediction";
import "./App.css";

function App() {
  const [page, setPage] = useState("dashboard");

  const renderPage = () => {
    if (page === "dashboard") {
      return <Dashboard />;
    }

    if (page === "customer") {
      return <CustomerSearch />;
    }

    if (page === "high-risk") {
      return <HighRisk />;
    }

    if (page === "features") {
      return <Features />;
    }

    if (page === "prediction") {
      return <Prediction />;
    }
  };

  return (
    <div className="app">

      <header className="header">
        <h1>Customer Retention Dashboard</h1>
      </header>

      <nav className="navbar">

        <button onClick={() => setPage("dashboard")}>
          Dashboard
        </button>

        <button onClick={() => setPage("customer")}>
          Customer Search
        </button>

        <button onClick={() => setPage("high-risk")}>
          High Risk
        </button>

        <button onClick={() => setPage("features")}>
          Customer Features
        </button>

        <button onClick={() => setPage("prediction")}>
          Prediction
        </button>

      </nav>

      <main className="container">
        {renderPage()}
      </main>

    </div>
  );
}

export default App;