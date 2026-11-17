import React, { useState, useEffect } from 'react';
import { getOptimization } from '../services/api';
import { PieChart, DollarSign, TrendingUp, Package, AlertCircle, Sliders, CheckCircle2 } from 'lucide-react';

export default function BudgetOptimizer() {
  const [totalBudget, setTotalBudget] = useState(500000);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const presetBudgets = [250000, 500000, 1000000, 2000000];

  useEffect(() => {
    const fetchPortfolioOptimization = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getOptimization(totalBudget);
        setResult(data);
      } catch (err) {
        console.error('Failed to load portfolio optimization:', err);
        setError('Failed to compute portfolio budget optimization from backend.');
      } finally {
        setLoading(false);
      }
    };

    if (totalBudget > 0) {
      fetchPortfolioOptimization();
    }
  }, [totalBudget]);

  return (
    <div className="calculator-card">
      <div className="calculator-header">
        <div className="calculator-title-group">
          <div className="calculator-icon">
            <PieChart size={22} />
          </div>
          <div>
            <h2>Portfolio Budget Optimizer</h2>
            <p>Distribute capital across travel inventory items by marginal expected profit per rupee (ROI)</p>
          </div>
        </div>
        <div className="calculator-badge">
          OPT-02 • Marginal ROI Allocation
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
            <Sliders size={16} /> Budget Configuration
          </h3>

          <div className="form-group">
            <label htmlFor="totalBudgetInput">Total Capital Budget ($):</label>
            <div className="input-with-icon">
              <DollarSign size={14} />
              <input
                id="totalBudgetInput"
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
            <span className="preset-label">Quick Presets:</span>
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

          {result && (
            <div className="economics-summary-box">
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

        {/* Results & Allocation Table */}
        <div className="calculator-results">
          {loading ? (
            <div className="loading-state">Optimizing portfolio allocations across items...</div>
          ) : result ? (
            <>
              <div className="kpi-grid">
                <div className="kpi-card highlight-kpi">
                  <div className="kpi-icon">
                    <DollarSign size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Total Budget</span>
                    <span className="kpi-value">${result.total_budget?.toLocaleString()}</span>
                    <span className="kpi-sub">Allocated: ${result.allocated_budget?.toLocaleString()}</span>
                  </div>
                </div>

                <div className="kpi-card success-kpi">
                  <div className="kpi-icon">
                    <TrendingUp size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Expected Portfolio Profit</span>
                    <span className="kpi-value">${result.total_expected_profit?.toLocaleString()}</span>
                    <span className="kpi-sub">Return on Capital: {(result.portfolio_roi * 100).toFixed(1)}%</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-icon">
                    <Package size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Funded Items</span>
                    <span className="kpi-value">
                      {result.allocations?.filter(a => a.allocated_budget > 0).length} / {result.allocations?.length}
                    </span>
                    <span className="kpi-sub">Optimized by Marginal ROI</span>
                  </div>
                </div>
              </div>

              <div className="breakdown-section">
                <h4>Optimal Item-Level Allocations</h4>
                <div className="table-responsive">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Item ID & Name</th>
                        <th>Type</th>
                        <th>Destination</th>
                        <th>Allocated Budget</th>
                        <th>Units Purchased</th>
                        <th>Expected Profit</th>
                        <th>ROI</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.allocations?.map((item, i) => (
                        <tr key={i} className={item.allocated_budget > 0 ? '' : 'zero-alloc-row'}>
                          <td>
                            <strong>{item.item_id}</strong>
                            <div className="sub-item-name">{item.item_name}</div>
                          </td>
                          <td>
                            <span className={`badge-type ${item.item_type}`}>
                              {item.item_type}
                            </span>
                          </td>
                          <td>{item.destination}</td>
                          <td><strong>${item.allocated_budget?.toLocaleString()}</strong></td>
                          <td>{item.units_purchased}</td>
                          <td className="profit-cell">${item.expected_profit?.toLocaleString()}</td>
                          <td>
                            <span className={item.roi > 0.2 ? 'high-roi' : ''}>
                              {(item.roi * 100).toFixed(1)}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="empty-state">Enter a budget to view portfolio allocation recommendations.</div>
          )}
        </div>
      </div>
    </div>
  );
}
