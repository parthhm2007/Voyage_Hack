import React, { useState, useEffect } from 'react';
import { getNewsvendor } from '../services/api';
import { Calculator, TrendingUp, IndianRupee, Package, AlertCircle, Sliders } from 'lucide-react';

export default function NewsvendorCalculator({ itemId, itemObj }) {
  const [unitCost, setUnitCost] = useState('');
  const [sellPrice, setSellPrice] = useState('');
  const [salvageValue, setSalvageValue] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Pre-populate economics when itemObj changes
  useEffect(() => {
    if (itemObj) {
      const cost = itemObj.base_supplier_cost ?? 100;
      const price = itemObj.base_sell_price ?? 150;

      setUnitCost(cost);
      setSellPrice(price);
      setSalvageValue(''); // Empty by default: let backend use central salvage config
    }
  }, [itemObj]);

  // Fetch newsvendor optimization results when item or parameters change
  useEffect(() => {
    if (!itemId) {
      setResult(null);
      return;
    }

    const fetchOptimization = async () => {
      try {
        setLoading(true);
        setError(null);
        const params = {};
        if (unitCost !== '') params.unit_cost = parseFloat(unitCost);
        if (sellPrice !== '') params.sell_price = parseFloat(sellPrice);
        if (salvageValue !== '') params.salvage_value = parseFloat(salvageValue);
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;

        const data = await getNewsvendor(itemId, params);
        setResult(data);
      } catch (err) {
        console.error('Failed to load newsvendor optimization:', err);
        setError('Failed to compute newsvendor optimization from backend.');
      } finally {
        setLoading(false);
      }
    };

    fetchOptimization();
  }, [itemId, unitCost, sellPrice, salvageValue, startDate, endDate]);

  if (!itemId) return null;

  const itemTypeLabel = itemObj?.item_type ? itemObj.item_type.toUpperCase() : 'ITEM';

  return (
    <div className="calculator-card">
      <div className="calculator-header">
        <div className="calculator-title-group">
          <div className="calculator-icon">
            <Calculator size={22} />
          </div>
          <div>
            <h2>Newsvendor Inventory Optimization</h2>
            <p>Calculate risk-adjusted pre-buy quantity (Q*), critical fractile, and expected profit</p>
          </div>
        </div>
        <div className="calculator-badge">
          {itemTypeLabel} • {itemObj?.destination || 'Global'}
        </div>
      </div>

      {error && (
        <div className="alert-banner error-banner">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="calculator-body">
        {/* Controls Sidebar / Form */}
        <div className="calculator-controls">
          <h3>
            <Sliders size={16} /> Unit Economics & Parameters
          </h3>
          
          <div className="form-group">
            <label htmlFor="unitCost">Unit Cost (c):</label>
            <div className="input-with-icon">
              <IndianRupee size={14} />
              <input
                id="unitCost"
                type="number"
                step="0.01"
                value={unitCost}
                onChange={(e) => setUnitCost(e.target.value)}
                placeholder="Supplier cost"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="sellPrice">Sell Price (p):</label>
            <div className="input-with-icon">
              <IndianRupee size={14} />
              <input
                id="sellPrice"
                type="number"
                step="0.01"
                value={sellPrice}
                onChange={(e) => setSellPrice(e.target.value)}
                placeholder="Sell price"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="salvageValue">Salvage Value (s):</label>
            <div className="input-with-icon">
              <IndianRupee size={14} />
              <input
                id="salvageValue"
                type="number"
                step="0.01"
                value={salvageValue}
                onChange={(e) => setSalvageValue(e.target.value)}
                placeholder="Salvage value"
              />
            </div>
            {result?.assumptions && (
              <small className="help-text">
                Assumptions: Salvage rate {(result.assumptions.salvage_rate * 100).toFixed(0)}% (₹{result.assumptions.salvage_value?.toLocaleString('en-IN', { maximumFractionDigits: 0 })})
              </small>
            )}
          </div>

          <div className="date-filter-group">
            <div className="form-group">
              <label htmlFor="startDate">Start Date:</label>
              <input
                id="startDate"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="endDate">End Date:</label>
              <input
                id="endDate"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>

          {result && (
            <div className="economics-summary-box">
              <div className="econ-row">
                <span>Critical Fractile (CR):</span>
                <strong>{result.critical_fractile}</strong>
              </div>
              <div className="econ-row">
                <span>Overage Cost (Co):</span>
                <strong>₹{Math.max(0, result.unit_cost - result.salvage_value).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>
              </div>
              <div className="econ-row">
                <span>Underage Cost (Cu):</span>
                <strong>₹{Math.max(0, result.sell_price - result.unit_cost).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>
              </div>
            </div>
          )}
        </div>

        {/* Results & KPI View */}
        <div className="calculator-results">
          {loading ? (
            <div className="loading-state">Computing optimal inventory strategy...</div>
          ) : result ? (
            <>
              {result.capacity_capped && (
                <div className="alert-banner info-banner" style={{ marginBottom: '1rem', padding: '0.75rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', borderRadius: '6px' }}>
                  <AlertCircle size={16} />
                  <span>Quantity capped at physical capacity ({result.capacity_per_day} units/day)</span>
                </div>
              )}

              <div className="kpi-grid">
                <div className="kpi-card highlight-kpi">
                  <div className="kpi-icon">
                    <Package size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Optimal Pre-Buy Q* (Avg)</span>
                    <span className="kpi-value">{result.optimal_quantity_avg}</span>
                    <span className="kpi-sub">Total Window: {result.total_optimal_quantity} units</span>
                    {result.capacity_capped && (
                      <span className="kpi-sub" style={{ color: '#d97706', fontWeight: 600 }}>Quantity capped at physical capacity</span>
                    )}
                  </div>
                </div>

                <div className="kpi-card success-kpi">
                  <div className="kpi-icon">
                    <TrendingUp size={20} />
                  </div>
                  <div className="kpi-content">
                    <span className="kpi-label">Expected Profit</span>
                    <span className="kpi-value">₹{result.total_expected_profit?.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                    <span className="kpi-sub">Across selected forecast window</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-content">
                    <span className="kpi-label">Expected Demand (Avg)</span>
                    <span className="kpi-value">{result.expected_demand_avg}</span>
                    <span className="kpi-sub">P50 Median Benchmark</span>
                  </div>
                </div>
              </div>

              <div className="breakdown-section">
                <h4>Daily Optimization Breakdown</h4>
                <div className="table-responsive">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>P10</th>
                        <th>P50</th>
                        <th>P90</th>
                        <th>Expected Demand</th>
                        <th>Optimal Q*</th>
                        <th>Expected Profit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.daily_breakdown?.slice(0, 15).map((row, i) => (
                        <tr key={i}>
                          <td>{row.date}</td>
                          <td>{row.p10}</td>
                          <td>{row.p50}</td>
                          <td>{row.p90}</td>
                          <td>{row.expected_demand}</td>
                          <td><strong>{row.optimal_quantity}</strong></td>
                          <td className="profit-cell">₹{row.expected_profit?.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {result.daily_breakdown?.length > 15 && (
                    <p className="table-note">Showing first 15 days of {result.daily_breakdown.length} total forecast days.</p>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="empty-state">Select an item and configure economics to view optimization results.</div>
          )}
        </div>
      </div>
    </div>
  );
}
