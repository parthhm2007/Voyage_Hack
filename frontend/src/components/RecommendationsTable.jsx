import React, { useState, useEffect } from 'react';
import { getOptimization } from '../services/api';
import { Table, DollarSign, TrendingUp, Package, AlertCircle, Sliders, ShieldAlert } from 'lucide-react';

export default function RecommendationsTable() {
  const [totalBudget, setTotalBudget] = useState(500000);
  const [riskAppetite, setRiskAppetite] = useState(0.5);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const presetBudgets = [250000, 500000, 1000000, 2000000];

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getOptimization(totalBudget, riskAppetite);
        setResult(data);
      } catch (err) {
        console.error('Failed to load portfolio recommendations:', err);
        setError('Failed to compute portfolio recommendations from backend.');
      } finally {
        setLoading(false);
      }
    };

    if (totalBudget > 0) {
      fetchRecommendations();
    }
  }, [totalBudget, riskAppetite]);

  const getRiskLabel = (val) => {
    if (val <= 0.25) return 'Conservative (P10 Heavy)';
    if (val <= 0.75) return 'Balanced (P50 Median)';
    return 'Aggressive (P90 Upside)';
  };

  return (
    <div className="calculator-card">
      <div className="calculator-header">
        <div className="calculator-title-group">
          <div className="calculator-icon">
            <Table size={22} />
          </div>
          <div>
            <h2>Portfolio Recommendations Table</h2>
            <p>Actionable inventory pre-buy recommendations connecting demand forecasts, budget constraints, and risk appetite</p>
          </div>
        </div>
        <div className="calculator-badge">
          UI-01 • Risk-Adjusted Allocation
        </div>
      </div>

      {error && (
        <div className="alert-banner error-banner">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="calculator-body">
        {/* Controls Sidebar */}
        <div className="calculator-controls">
          <h3>
            <Sliders size={16} /> Decision Controls
          </h3>

          <div className="form-group">
            <label htmlFor="recBudgetInput">Total Capital Budget ($):</label>
            <div className="input-with-icon">
              <DollarSign size={14} />
              <input
                id="recBudgetInput"
                type="number"
                step="10000"
                min="1000"
                value={totalBudget}
                onChange={(e) => setTotalBudget(parseFloat(e.target.value) || 0)}
                placeholder="Enter total budget"
              />
            </div>
          </div>

          <div className="preset-buttons">
            <span className="preset-label">Budget Presets:</span>
            <div className="preset-grid">
              {presetBudgets.map((b) => (
                <button
                  key={b}
                  type="button"
                  className={`preset-btn ${totalBudget === b ? 'active-preset' : ''}`}
                  onClick={() => setTotalBudget(b)}
                >
                  ${(b / 1000).toFixed(0)}k
                </button>
              ))}
            </div>
          </div>

          <div className="form-group" style={{ marginTop: '1.25rem' }}>
            <label htmlFor="riskSlider">
              Risk Appetite: <strong>{riskAppetite.toFixed(2)}</strong>
            </label>
            <input
              id="riskSlider"
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={riskAppetite}
              onChange={(e) => setRiskAppetite(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--primary-color, #2563eb)', cursor: 'pointer' }}
            />
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted, #64748b)', marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <ShieldAlert size={13} />
              <span>{getRiskLabel(riskAppetite)}</span>
            </div>
          </div>

          {result && (
            <div className="economics-summary-box" style={{ marginTop: '1.25rem' }}>
              <div className="econ-row">
                <span>Allocated Budget:</span>
                <strong>${result.allocated_budget?.toLocaleString()}</strong>
              </div>
              <div className="econ-row">
                <span>Unallocated Cash:</span>
                <strong>${Math.max(0, result.total_budget - result.allocated_budget).toLocaleString()}</strong>
              </div>
              <div className="econ-row">
                <span>Portfolio ROI:</span>
                <strong className="success-text">{(result.portfolio_roi * 100).toFixed(2)}%</strong>
              </div>
            </div>
          )}
        </div>

        {/* Results & Recommendations Table */}
        <div className="calculator-results">
          {loading ? (
            <div className="loading-state">Computing risk-adjusted inventory recommendations...</div>
          ) : result ? (
            <>
              <div className="kpi-grid">
                <div className="kpi-card highlight-kpi">
                  <div className="kpi-icon">
                    <DollarSign size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Capital Deployed</span>
                    <span className="kpi-value">${result.allocated_budget?.toLocaleString()}</span>
                    <span className="kpi-sub">Budget: ${result.total_budget?.toLocaleString()}</span>
                  </div>
                </div>

                <div className="kpi-card success-kpi">
                  <div className="kpi-icon">
                    <TrendingUp size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Expected Portfolio Profit</span>
                    <span className="kpi-value">${result.total_expected_profit?.toLocaleString()}</span>
                    <span className="kpi-sub">Portfolio ROI: {(result.portfolio_roi * 100).toFixed(1)}%</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-icon">
                    <Package size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Active Allocations</span>
                    <span className="kpi-value">
                      {result.allocations?.filter(a => a.allocated_budget > 0).length} / {result.allocations?.length}
                    </span>
                    <span className="kpi-sub">Risk Profile: {riskAppetite <= 0.25 ? 'Conservative' : riskAppetite <= 0.75 ? 'Balanced' : 'Aggressive'}</span>
                  </div>
                </div>
              </div>

              <div className="table-container" style={{ marginTop: '1.5rem', overflowX: 'auto' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Item ID & Name</th>
                      <th>Type</th>
                      <th>Destination</th>
                      <th>Allocated Budget</th>
                      <th>Units Q*</th>
                      <th>Expected Profit</th>
                      <th>ROI %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.allocations?.map((item) => (
                      <tr key={item.item_id}>
                        <td>
                          <strong>{item.item_name}</strong>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted, #64748b)' }}>{item.item_id}</div>
                        </td>
                        <td>
                          <span className={`badge badge-${item.item_type}`}>
                            {item.item_type}
                          </span>
                        </td>
                        <td>{item.destination}</td>
                        <td><strong>${item.allocated_budget?.toLocaleString()}</strong></td>
                        <td>{item.units_purchased?.toLocaleString()}</td>
                        <td className="success-text"><strong>${item.expected_profit?.toLocaleString()}</strong></td>
                        <td>
                          <span className={item.roi > 0.2 ? 'badge-success' : ''}>
                            {(item.roi * 100).toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="empty-state">No recommendation data available. Adjust budget to compute.</div>
          )}
        </div>
      </div>
    </div>
  );
}
