import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const dataPoint = payload[0].payload;
    return (
      <div className="custom-chart-tooltip">
        <div className="tooltip-date">Date: {label}</div>
        {dataPoint.item_id && (
          <div className="tooltip-row">
            <span>Item ID:</span> <strong>{dataPoint.item_id}</strong>
          </div>
        )}
        <div className="tooltip-row" style={{ color: '#6366f1' }}>
          <span>P50 Forecast:</span>
          <strong>{Number(dataPoint.p50)?.toFixed(1)}</strong>
        </div>
        <div className="tooltip-row" style={{ color: '#3b82f6' }}>
          <span>P10 (Low):</span>
          <strong>{Number(dataPoint.p10)?.toFixed(1)}</strong>
        </div>
        <div className="tooltip-row" style={{ color: '#1d4ed8' }}>
          <span>P90 (High):</span>
          <strong>{Number(dataPoint.p90)?.toFixed(1)}</strong>
        </div>
      </div>
    );
  }
  return null;
};

export default function ForecastChart({ data = [], selectedItemName = '' }) {
  if (!data || data.length === 0) {
    return (
      <div className="chart-empty">
        <p>No 90-day forecast data available for the selected item.</p>
      </div>
    );
  }

  // Transform data to ensure confidence range format [p10, p90] for Recharts Area
  const chartData = data.map(d => ({
    ...d,
    confidenceRange: [Number(d.p10) || 0, Number(d.p90) || 0],
    p50: Number(d.p50) || 0,
    p10: Number(d.p10) || 0,
    p90: Number(d.p90) || 0,
  }));

  return (
    <div className="chart-card">
      <div className="chart-header">
        <h3 className="chart-title">
          90-Day Demand Forecast (P50 & P10-P90 Band) {selectedItemName && `- ${selectedItemName}`}
        </h3>
        <div className="chart-legend">
          <span className="legend-badge">
            <span className="legend-square-searches" style={{ backgroundColor: '#93c5fd' }}></span>
            <span>P10 - P90 Confidence Band</span>
          </span>
          <span className="legend-badge">
            <span className="legend-circle-bookings" style={{ backgroundColor: '#6366f1' }}></span>
            <span>P50 Expected Demand</span>
          </span>
        </div>
      </div>

      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area
              type="monotone"
              dataKey="confidenceRange"
              name="P10-P90 Confidence Band"
              fill="#93c5fd"
              fillOpacity={0.3}
              stroke="#60a5fa"
              strokeWidth={1}
            />
            <Line
              type="monotone"
              dataKey="p50"
              name="P50 Forecast"
              stroke="#6366f1"
              strokeWidth={2}
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
