import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

/**
 * Defensive pure function aggregating records by date when multiple item_ids are present.
 * Sums bookings and searches; sold_out_flag is 1 if any record that day was sold out.
 */
export function aggregateHistoryByDate(records = []) {
  if (!records || records.length === 0) return [];
  const map = new Map();
  for (const r of records) {
    if (!map.has(r.date)) {
      map.set(r.date, {
        date: r.date,
        searches: Number(r.searches) || 0,
        bookings: Number(r.bookings) || 0,
        sold_out_flag: Number(r.sold_out_flag) === 1 ? 1 : 0,
      });
    } else {
      const entry = map.get(r.date);
      entry.searches += Number(r.searches) || 0;
      entry.bookings += Number(r.bookings) || 0;
      if (Number(r.sold_out_flag) === 1) {
        entry.sold_out_flag = 1;
      }
    }
  }
  return Array.from(map.values()).sort((a, b) => a.date.localeCompare(b.date));
}

// Custom dot renderer for sold-out days on the bookings line (F11: distinct colour, no text)
const renderSoldOutDot = (props) => {
  const { cx, cy, payload } = props;
  if (payload && payload.sold_out_flag === 1 && cx != null && cy != null) {
    return (
      <circle
        key={`soldout-dot-${payload.date}`}
        cx={cx}
        cy={cy}
        r={5}
        fill="#f43f5e"
        stroke="#ffffff"
        strokeWidth={2}
      />
    );
  }
  return null;
};

// Custom Tooltip showing "Sold out" alert on hover (F11)
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const dataPoint = payload[0].payload;
    const isSoldOut = dataPoint && dataPoint.sold_out_flag === 1;
    return (
      <div className="custom-chart-tooltip">
        <div className="tooltip-date">Date: {label}</div>
        {payload.map((entry, index) => (
          <div key={`entry-${index}`} className="tooltip-row" style={{ color: entry.color }}>
            <span>{entry.name}:</span>
            <strong>{entry.value?.toLocaleString()}</strong>
          </div>
        ))}
        {isSoldOut && (
          <div className="tooltip-sold-out-alert">
            Status: Sold out
          </div>
        )}
      </div>
    );
  }
  return null;
};

export default function BookingsChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="chart-empty">
        <p>No historical data available for the selected filters.</p>
      </div>
    );
  }

  // Ensure chart never receives more than one record per date (F4)
  const uniqueItems = new Set(data.map(d => d.item_id).filter(Boolean));
  const chartData = uniqueItems.size > 1 ? aggregateHistoryByDate(data) : data;

  return (
    <div className="chart-card">
      <div className="chart-header">
        <h3 className="chart-title">Bookings vs Searches Over Time</h3>
        <div className="chart-legend">
          <span className="legend-badge">
            <span className="legend-square-searches"></span>
            <span>Searches</span>
          </span>
          <span className="legend-badge">
            <span className="legend-circle-bookings"></span>
            <span>Bookings</span>
          </span>
          <span className="legend-badge">
            <span className="legend-circle-soldout"></span>
            <span>Sold Out Day</span>
          </span>
        </div>
      </div>

      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
            <YAxis yAxisId="left" stroke="#94a3b8" fontSize={12} />
            <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" fontSize={12} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar yAxisId="left" dataKey="searches" name="Searches" fill="#6366f1" opacity={0.6} barSize={20} />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="bookings"
              name="Bookings"
              stroke="#10b981"
              strokeWidth={2}
              dot={renderSoldOutDot}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
