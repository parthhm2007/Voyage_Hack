import React, { useState, useEffect, useMemo } from 'react';
import { getOptimization } from '../services/api';
import { Table, IndianRupee, TrendingUp, Package, AlertCircle, Sliders, ShieldAlert, Info, AlertTriangle } from 'lucide-react';

export const DEBOUNCE_DELAY_MS = 300;
export const MAX_BUDGET = 1_000_000_000;

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

export default function RecommendationsTable() {
  const [budgetText, setBudgetText] = useState('500000');
  const [riskAppetite, setRiskAppetite] = useState(0.5);
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

  // Validation
  const validationError = useMemo(() => {
    const trimmed = String(budgetText).trim();
    if (!trimmed) {
      return 'Please enter a total capital budget.';
    }
    const num = Number(trimmed);
    if (isNaN(num)) {
      return 'Budget must be a valid number.';
    }
    if (num < 0) {
      return 'Budget cannot be negative.';
    }
    if (num > MAX_BUDGET) {
      return `Budget cannot exceed ₹${MAX_BUDGET.toLocaleString('en-IN')}.`;
    }
    return null;
  }, [budgetText]);

  const numericBudget = useMemo(() => {
    if (validationError) return null;
    const num = Number(budgetText);
    return Math.floor(num);
  }, [budgetText, validationError]);

  const handleBudgetChange = (e) => {
    const val = e.target.value;
    setBudgetText(val);
  };

  const handlePresetClick = (b) => {
    setBudgetText(String(b));
  };

  const handleRetry = () => {
    setRetryTrigger((prev) => prev + 1);
  };

  const getRiskLabel = (val) => {
    if (val <= 0.25) return 'Conservative (P10 Heavy)';
    if (val <= 0.75) return 'Balanced (P50 Median)';
    return 'Aggressive (P90 Upside)';
  };

  // Debounced fetch with AbortController and active flag
  useEffect(() => {
    if (validationError || numericBudget === null) {
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
        const data = await getOptimization(numericBudget, riskAppetite, {}, controller.signal);
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
          setError('Failed to compute portfolio recommendations from backend.');
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
  }, [numericBudget, riskAppetite, retryTrigger, validationError]);

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
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
          <button
            type="button"
            className="alert-retry-btn"
            onClick={handleRetry}
            style={{ minHeight: '36px' }}
          >
            Retry
          </button>
        </div>
      )}

      {validationError && (
        <div className="alert-banner" style={{ backgroundColor: '#fffbeb', color: '#b45309', borderColor: '#fde68a' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={18} />
            <span>{validationError}</span>
          </div>
        </div>
      )}

      {result?.note && (
        <div className="alert-banner" style={{ backgroundColor: '#f0f9ff', color: '#0369a1', borderColor: '#bae6fd' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Info size={18} />
            <span>{result.note}</span>
          </div>
        </div>
      )}

      <div className="calculator-body">
        {/* Controls Sidebar */}
        <div className="calculator-controls">
          <h3>
            <Sliders size={16} /> Decision Controls
          </h3>

          <div className="form-group">
            <label htmlFor="recBudgetInput">Total Capital Budget (₹):</label>
            <div className="input-with-icon">
              <IndianRupee size={14} />
              <input
                id="recBudgetInput"
                type="number"
                step="10000"
                min="0"
                max={MAX_BUDGET}
                value={budgetText}
                onChange={handleBudgetChange}
                placeholder="Enter total budget in ₹"
                style={{ minHeight: '40px' }}
              />
            </div>
          </div>

          <div className="preset-buttons">
            <span className="preset-label">Budget Presets:</span>
            <div className="preset-grid preset-buttons-grid">
              {presetBudgets.map((b) => (
                <button
                  key={b}
                  type="button"
                  className={`preset-btn ${numericBudget === b ? 'active' : ''}`}
                  onClick={() => handlePresetClick(b)}
                  style={{ minHeight: '40px' }}
                >
                  {getPresetLabel(b)}
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
              aria-label="Risk appetite"
              aria-valuemin="0"
              aria-valuemax="1"
              aria-valuenow={riskAppetite}
              aria-valuetext={getRiskLabel(riskAppetite)}
              style={{ width: '100%', accentColor: 'var(--primary-color, #2563eb)', cursor: 'pointer', minHeight: '40px' }}
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

          {/* Assumptions Box */}
          {result?.assumptions && (
            <div className="assumptions-box" style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '0.75rem', color: '#475569' }}>
              <div style={{ fontWeight: 600, marginBottom: '0.35rem', color: '#1e293b' }}>Optimization Assumptions</div>
              <div>Salvage: Hotels {((result.assumptions.salvage_rates?.hotel ?? 0.4) * 100).toFixed(0)}%, Flights {((result.assumptions.salvage_rates?.flight ?? 0.15) * 100).toFixed(0)}%</div>
              <div>Scenario Weights: P10 {((result.assumptions.risk_weights?.p10 ?? 0.25) * 100).toFixed(0)}%, P50 {((result.assumptions.risk_weights?.p50 ?? 0.5) * 100).toFixed(0)}%, P90 {((result.assumptions.risk_weights?.p90 ?? 0.25) * 100).toFixed(0)}%</div>
              <div>Window: {result.assumptions.days} days ({result.assumptions.start_date} to {result.assumptions.end_date})</div>
              {result.excluded && result.excluded.length > 0 && (
                <div style={{ marginTop: '0.35rem', color: '#d97706' }} title={result.excluded.map(e => `${e.item_id}: ${e.reason}`).join(', ')}>
                  Excluded: {result.excluded.length} items (non-positive profit)
                </div>
              )}
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
                    <IndianRupee size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Capital Deployed</span>
                    <span className="kpi-value">{formatRupee(result.allocated_budget)}</span>
                    <span className="kpi-sub">Budget: {formatRupee(result.total_budget)}</span>
                  </div>
                </div>

                <div className="kpi-card success-kpi">
                  <div className="kpi-icon">
                    <TrendingUp size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Expected Portfolio Profit</span>
                    <span className="kpi-value">{formatRupee(result.total_expected_profit)}</span>
                    <span className="kpi-sub">Portfolio ROI: {formatPercent(result.portfolio_roi, 1)}</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-icon">
                    <Package size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Active Allocations</span>
                    <span className="kpi-value">
                      {result.allocations ? `${result.allocations.filter(a => a.allocated_budget > 0).length} / ${result.allocations.length}` : '—'}
                    </span>
                    <span className="kpi-sub">Risk Profile: {riskAppetite <= 0.25 ? 'Conservative' : riskAppetite <= 0.75 ? 'Balanced' : 'Aggressive'}</span>
                  </div>
                </div>
              </div>

              <div className="table-container" style={{ marginTop: '1.5rem', overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Item ID & Name</th>
                      <th>Type</th>
                      <th>Destination</th>
                      <th>Unit Cost</th>
                      <th>Units Q*</th>
                      <th>Allocated Budget</th>
                      <th>Expected Profit</th>
                      <th>ROI %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.allocations?.map((item) => (
                      <tr key={item.item_id}>
                        <td>
                          <div style={{ maxWidth: '170px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={item.item_name}>
                            <strong>{item.item_name}</strong>
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted, #64748b)' }}>
                            {item.item_id}
                            {item.capacity_capped && (
                              <span style={{ marginLeft: '6px', fontSize: '0.7rem', padding: '1px 4px', backgroundColor: '#fed7aa', color: '#9a3412', borderRadius: '3px' }} title="Allocated units reached maximum physical capacity">
                                Cap Reached
                              </span>
                            )}
                          </div>
                        </td>
                        <td>
                          <span className={`badge ${item.item_type}`}>
                            {item.item_type}
                          </span>
                        </td>
                        <td>{item.destination}</td>
                        <td>{formatRupee(item.unit_cost)}</td>
                        <td><strong>{formatNumber(item.units_purchased)}</strong></td>
                        <td><strong>{formatRupee(item.allocated_budget)}</strong></td>
                        <td className="success-text"><strong>{formatRupee(item.expected_profit)}</strong></td>
                        <td>
                          <span className={item.roi > 0.2 ? 'badge-success' : ''}>
                            {formatPercent(item.roi, 1)}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {(!result.allocations || result.allocations.length === 0) && (
                      <tr>
                        <td colSpan="8" style={{ textAlign: 'center', padding: '1.5rem', color: '#64748b' }}>
                          No allocations available for the current configuration.
                        </td>
                      </tr>
                    )}
                  </tbody>
                  {result.allocations && result.allocations.length > 0 && (
                    <tfoot>
                      <tr style={{ fontWeight: 600, borderTop: '2px solid #cbd5e1', backgroundColor: '#f8fafc' }}>
                        <td colSpan="4">Total Portfolio Summary</td>
                        <td>{formatNumber(result.allocations.reduce((sum, a) => sum + (a.units_purchased || 0), 0))}</td>
                        <td>{formatRupee(result.allocated_budget)}</td>
                        <td className="success-text">{formatRupee(result.total_expected_profit)}</td>
                        <td>{formatPercent(result.portfolio_roi, 1)}</td>
                      </tr>
                    </tfoot>
                  )}
                </table>
              </div>
            </>
          ) : (
            <div className="empty-state">
              {validationError ? validationError : 'No recommendation data available. Enter a budget to compute.'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
