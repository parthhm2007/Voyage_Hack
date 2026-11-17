import React, { useState, useEffect } from 'react';
import { getOptimization } from '../services/api';
import { PieChart, IndianRupee, TrendingUp, Package, AlertCircle, Sliders } from 'lucide-react';

export const DEBOUNCE_DELAY_MS = 300;

export const formatRupee = (val) => {
  if (val === null || val === undefined || isNaN(val) || !isFinite(val)) {
    return '—';
  }
  return `₹${Math.round(Number(val)).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
};

export const formatNumber = (val, maxDecimals = 0) => {
  if (val === null || val === undefined || isNaN(val) || !isFinite(val)) {
    return '—';
  }
  return Number(val).toLocaleString('en-IN', { maximumFractionDigits: maxDecimals });
};

export const formatPercent = (val, maxDecimals = 1) => {
  if (val === null || val === undefined || isNaN(val) || !isFinite(val)) {
    return '—';
  }
  return `${(Number(val) * 100).toFixed(maxDecimals)}%`;
};

export default function BudgetOptimizer() {
  const [totalBudget, setTotalBudget] = useState(500000);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retryTrigger, setRetryTrigger] = useState(0);

  const presetBudgets = [250000, 500000, 1000000, 2000000];

  const getPresetLabel = (b) => {
    if (b >= 100000) {
      const lakhs = b / 100000;
      return `₹${lakhs % 1 === 0 ? lakhs.toFixed(0) : lakhs.toFixed(1)}L`;
    }
    return `₹${(b / 1000).toFixed(0)}k`;
  };

  useEffect(() => {
    if (totalBudget <= 0) {
      setResult(null);
      setLoading(false);
      return;
    }

    let active = true;
    const controller = new AbortController();

    setLoading(true);
    setError(null);

    const timer = setTimeout(async () => {
      try {
        const data = await getOptimization(totalBudget, 0.5, {}, controller.signal);
        if (active) {
          setResult(data);
          setError(null);
        }
      } catch (err) {
        if (err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED') {
          return;
        }
        if (active) {
          setResult(null);
          setError('Failed to compute portfolio budget optimization from backend.');
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }, DEBOUNCE_DELAY_MS);

    return () => {
      active = false;
      clearTimeout(timer);
      controller.abort();
    };
  }, [totalBudget, retryTrigger]);

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
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
          <button
            type="button"
            className="alert-retry-btn"
            onClick={() => setRetryTrigger((c) => c + 1)}
            style={{ minHeight: '36px' }}
          >
            Retry
          </button>
        </div>
      )}

      <div className="calculator-body">
        {/* Controls Sidebar */}
        <div className="calculator-controls">
          <h3>
            <Sliders size={16} /> Budget Configuration
          </h3>

          <div className="form-group">
            <label htmlFor="totalBudgetInput">Total Capital Budget (₹):</label>
            <div className="input-with-icon">
              <IndianRupee size={14} />
              <input
                id="totalBudgetInput"
                type="number"
                step="10000"
                min="0"
                value={totalBudget}
                onChange={(e) => setTotalBudget(parseFloat(e.target.value) || 0)}
                placeholder="Enter total budget in ₹"
                style={{ minHeight: '40px' }}
              />
            </div>
          </div>

          <div className="preset-buttons">
            <span className="preset-label">Quick Presets:</span>
            <div className="preset-grid preset-buttons-grid">
              {presetBudgets.map((b) => (
                <button
                  key={b}
                  type="button"
                  className={`preset-btn ${totalBudget === b ? 'active' : ''}`}
                  onClick={() => setTotalBudget(b)}
                  style={{ minHeight: '40px' }}
                >
                  {getPresetLabel(b)}
                </button>
              ))}
            </div>
          </div>

          {result && (
            <div className="economics-summary-box">
              <div className="econ-row">
                <span>Allocated Budget:</span>
                <strong>{formatRupee(result.allocated_budget)}</strong>
              </div>
              <div className="econ-row">
                <span>Unallocated Cash:</span>
                <strong>{formatRupee(Math.max(0, result.total_budget - result.allocated_budget))}</strong>
              </div>
              <div className="econ-row">
                <span>Portfolio ROI:</span>
                <strong className="success-text">{formatPercent(result.portfolio_roi, 2)}</strong>
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
                    <IndianRupee size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Total Budget</span>
                    <span className="kpi-value">{formatRupee(result.total_budget)}</span>
                    <span className="kpi-sub">Allocated: {formatRupee(result.allocated_budget)}</span>
                  </div>
                </div>

                <div className="kpi-card success-kpi">
                  <div className="kpi-icon">
                    <TrendingUp size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Expected Portfolio Profit</span>
                    <span className="kpi-value">{formatRupee(result.total_expected_profit)}</span>
                    <span className="kpi-sub">Return on Capital: {formatPercent(result.portfolio_roi, 1)}</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-icon">
                    <Package size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Funded Items</span>
                    <span className="kpi-value">
                      {result.allocations ? `${result.allocations.filter(a => a.allocated_budget > 0).length} / ${result.allocations.length}` : '—'}
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
                      {result.allocations?.map((item) => (
                        <tr key={item.item_id} className={item.allocated_budget > 0 ? '' : 'zero-alloc-row'}>
                          <td>
                            <strong>{item.item_id}</strong>
                            <div className="sub-item-name">{item.item_name}</div>
                          </td>
                          <td>
                            <span className={`badge ${item.item_type}`}>
                              {item.item_type}
                            </span>
                          </td>
                          <td>{item.destination}</td>
                          <td><strong>{formatRupee(item.allocated_budget)}</strong></td>
                          <td>{formatNumber(item.units_purchased)}</td>
                          <td className="profit-cell">{formatRupee(item.expected_profit)}</td>
                          <td>
                            <span className={item.roi > 0.2 ? 'high-roi' : ''}>
                              {formatPercent(item.roi, 1)}
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
