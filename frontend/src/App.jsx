import { useState } from "react";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("Dashboard");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const [form, setForm] = useState({
    emp_id: "",
    name: "",
    amount: "",
    category: "Meals",
    description: "",
    date: "",
    has_preapproval: false,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const analyzeExpense = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...form,
          amount: Number(form.amount),
        }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
      alert("Backend connection failed. Make sure FastAPI is running.");
    }

    setLoading(false);
  };

  const decision = result?.decision?.decision || "PENDING";

  return (
    <div className="app">

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-icon">A</div>
          <div>
            <h2>AIONOS</h2>
            <span>AI Finance Factory</span>
          </div>
        </div>

        <nav>
          {["Dashboard", "Submit Expense", "Reports"].map((item) => (
            <button
              key={item}
              className={activeTab === item ? "nav-item active" : "nav-item"}
              onClick={() => setActiveTab(item)}
            >
              <span>
                {item === "Dashboard" && "⌂"}
                {item === "Submit Expense" && "+"}
                {item === "Reports" && "▣"}
              </span>
              {item}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="ai-status">
            <span className="status-dot"></span>
            <div>
              <strong>Agent Online</strong>
              <small>Expense engine active</small>
            </div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="main">

        <header className="topbar">
          <div>
            <p className="eyebrow">FINANCE OPERATIONS</p>
            <h1>{activeTab}</h1>
          </div>

          <div className="topbar-right">
            <div className="live">
              <span></span> Live
            </div>
            <div className="avatar">TS</div>
          </div>
        </header>

        {activeTab === "Dashboard" && (
          <>
            <section className="hero">
              <div>
                <p className="eyebrow">SMART EXPENSE CONTROL</p>
                <h2>AI-powered expense decisions.</h2>
                <p>
                  Submit an expense and let the approval agent evaluate
                  policy compliance, anomalies, risk, and the final decision.
                </p>
                <button
                  className="primary-btn"
                  onClick={() => setActiveTab("Submit Expense")}
                >
                  Analyze Expense →
                </button>
              </div>

              <div className="hero-orb">
                <div className="orb-core">AI</div>
                <div className="orb-ring ring-one"></div>
                <div className="orb-ring ring-two"></div>
              </div>
            </section>

            <section className="stats">
              <div className="stat-card">
                <span>Total Claims</span>
                <strong>24</strong>
                <small>This month</small>
              </div>

              <div className="stat-card">
                <span>Approved</span>
                <strong>18</strong>
                <small>75% of claims</small>
              </div>

              <div className="stat-card">
                <span>Flagged</span>
                <strong>4</strong>
                <small>Needs review</small>
              </div>

              <div className="stat-card">
                <span>Rejected</span>
                <strong>2</strong>
                <small>Policy violations</small>
              </div>
            </section>

            <section className="dashboard-grid">
              <div className="panel">
                <div className="panel-header">
                  <div>
                    <p className="eyebrow">AGENT PIPELINE</p>
                    <h3>Decision workflow</h3>
                  </div>
                  <span className="pill">AUTOMATED</span>
                </div>

                <div className="pipeline">
                  <div className="pipeline-step">
                    <b>01</b>
                    <div>
                      <strong>Expense Claim</strong>
                      <span>Claim details received</span>
                    </div>
                  </div>

                  <div className="line"></div>

                  <div className="pipeline-step">
                    <b>02</b>
                    <div>
                      <strong>Policy Check</strong>
                      <span>Rules and limits evaluated</span>
                    </div>
                  </div>

                  <div className="line"></div>

                  <div className="pipeline-step">
                    <b>03</b>
                    <div>
                      <strong>Anomaly Detection</strong>
                      <span>Unusual patterns identified</span>
                    </div>
                  </div>

                  <div className="line"></div>

                  <div className="pipeline-step">
                    <b>04</b>
                    <div>
                      <strong>Agent Decision</strong>
                      <span>Final approval recommendation</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <p className="eyebrow">RECENT ACTIVITY</p>
                    <h3>Latest claims</h3>
                  </div>
                </div>

                <div className="claim">
                  <div className="claim-avatar">PS</div>
                  <div className="claim-info">
                    <strong>Priya Sharma</strong>
                    <span>Meals · ₹850</span>
                  </div>
                  <span className="badge approved">APPROVED</span>
                </div>

                <div className="claim">
                  <div className="claim-avatar">RS</div>
                  <div className="claim-info">
                    <strong>Rahul Singh</strong>
                    <span>Travel · ₹18,000</span>
                  </div>
                  <span className="badge rejected">REJECTED</span>
                </div>

                <div className="claim">
                  <div className="claim-avatar">AK</div>
                  <div className="claim-info">
                    <strong>Ananya Kapoor</strong>
                    <span>Office Supplies · ₹1,950</span>
                  </div>
                  <span className="badge flagged">FLAGGED</span>
                </div>
              </div>
            </section>
          </>
        )}

        {activeTab === "Submit Expense" && (
          <section className="expense-layout">

            <div className="panel form-panel">
              <div className="panel-header">
                <div>
                  <p className="eyebrow">NEW CLAIM</p>
                  <h3>Submit an expense</h3>
                </div>
                <span className="pill">AI ANALYSIS</span>
              </div>

              <form onSubmit={analyzeExpense}>

                <div className="form-grid">
                  <label>
                    Employee ID
                    <input
                      name="emp_id"
                      placeholder="E101"
                      value={form.emp_id}
                      onChange={handleChange}
                      required
                    />
                  </label>

                  <label>
                    Employee Name
                    <input
                      name="name"
                      placeholder="Priya Sharma"
                      value={form.name}
                      onChange={handleChange}
                      required
                    />
                  </label>

                  <label>
                    Amount
                    <input
                      name="amount"
                      type="number"
                      placeholder="850"
                      value={form.amount}
                      onChange={handleChange}
                      required
                    />
                  </label>

                  <label>
                    Category
                    <select
                      name="category"
                      value={form.category}
                      onChange={handleChange}
                    >
                      <option>Meals</option>
                      <option>Travel</option>
                      <option>Office Supplies</option>
                      <option>Client Entertainment</option>
                      <option>Software/Subscriptions</option>
                    </select>
                  </label>

                  <label>
                    Date
                    <input
                      name="date"
                      type="date"
                      value={form.date}
                      onChange={handleChange}
                      required
                    />
                  </label>

                  <label>
                    Description
                    <input
                      name="description"
                      placeholder="Team lunch with client"
                      value={form.description}
                      onChange={handleChange}
                      required
                    />
                  </label>
                </div>

                <label className="checkbox">
                  <input
                    name="has_preapproval"
                    type="checkbox"
                    checked={form.has_preapproval}
                    onChange={handleChange}
                  />
                  <span>Expense has prior manager approval</span>
                </label>

                <button className="primary-btn full" disabled={loading}>
                  {loading ? "Analyzing..." : "Run AI Analysis →"}
                </button>
              </form>
            </div>

            <div className="panel result-panel">
              <p className="eyebrow">AGENT RESULT</p>

              {!result && (
                <div className="empty-result">
                  <div className="empty-icon">✦</div>
                  <h3>Waiting for an expense</h3>
                  <p>
                    Submit a claim to see policy checks, anomaly detection,
                    risk analysis and the agent decision.
                  </p>
                </div>
              )}

              {result && (
                <div className="result-content">
                  <div className={`decision ${decision.toLowerCase()}`}>
                    <span>AGENT DECISION</span>
                    <strong>{decision.replaceAll("_", " ")}</strong>
                  </div>

                  <div className="risk-box">
                    <span>Risk Score</span>
                    <strong>
                      {result.decision?.risk_score ?? 0}
                    </strong>
                    <small>/ 100</small>
                  </div>

                  <div className="result-section">
                    <h4>Policy Violations</h4>
                    {result.policy_violations?.length ? (
                      result.policy_violations.map((item, index) => (
                        <div className="issue" key={index}>
                          ⚠ {item}
                        </div>
                      ))
                    ) : (
                      <div className="success-message">
                        ✓ No policy violations
                      </div>
                    )}
                  </div>

                  <div className="result-section">
                    <h4>Anomalies</h4>
                    {result.anomalies?.length ? (
                      result.anomalies.map((item, index) => (
                        <div className="issue" key={index}>
                          ◇ {item}
                        </div>
                      ))
                    ) : (
                      <div className="success-message">
                        ✓ No anomalies detected
                      </div>
                    )}
                  </div>

                  <div className="result-section">
                    <h4>Agent Reasoning</h4>
                    <p className="reasoning">
                      {result.decision?.reasoning ||
                        "No reasoning returned."}
                    </p>
                  </div>
                </div>
              )}
            </div>

          </section>
        )}

        {activeTab === "Reports" && (
          <section className="panel reports-panel">
            <p className="eyebrow">MONTHLY OVERVIEW</p>
            <h3>Expense Report</h3>

            <div className="report-cards">
              <div>
                <span>Total Spend</span>
                <strong>₹23,300</strong>
              </div>
              <div>
                <span>Approved Claims</span>
                <strong>18</strong>
              </div>
              <div>
                <span>Flagged Claims</span>
                <strong>4</strong>
              </div>
              <div>
                <span>Rejected Claims</span>
                <strong>2</strong>
              </div>
            </div>

            <div className="report-message">
              <span>✦</span>
              AI monitoring is active across submitted expenses.
            </div>
          </section>
        )}

      </main>
    </div>
  );
}

export default App;