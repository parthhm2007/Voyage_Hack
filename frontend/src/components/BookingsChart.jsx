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
  Legend,
  ReferenceDot
} from 'recharts';

export default function BookingsChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center justify-center h-80">
        <p className="text-gray-500 font-medium">No historical data available for the selected filters.</p>
      </div>
    );
  }

  // Filter out or identify sold-out days for ReferenceDot highlighting
  const soldOutPoints = data.filter(item => item.sold_out_flag === 1);

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Bookings vs Searches Over Time</h3>
        <div className="flex items-center space-x-4 text-xs font-medium">
          <span className="flex items-center space-x-1">
            <span className="w-3 h-3 bg-indigo-500 rounded-sm inline-block"></span>
            <span className="text-gray-600">Searches</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-3 h-3 bg-emerald-500 rounded-full inline-block"></span>
            <span className="text-gray-600">Bookings</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-3 h-3 bg-rose-500 rounded-full inline-block"></span>
            <span className="text-gray-600">Sold Out Day</span>
          </span>
        </div>
      </div>

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
            <YAxis yAxisId="left" stroke="#9ca3af" fontSize={12} />
            <YAxis yAxisId="right" orientation="right" stroke="#9ca3af" fontSize={12} />
            <Tooltip
              contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '0.5rem', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              formatter={(value, name) => [value, name === 'searches' ? 'Searches' : 'Bookings']}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Legend />
            <Bar yAxisId="left" dataKey="searches" name="Searches" fill="#6366f1" opacity={0.6} barSize={20} />
            <Line yAxisId="right" type="monotone" dataKey="bookings" name="Bookings" stroke="#10b981" strokeWidth={2} dot={false} />
            
            {/* Highlight sold-out days */}
            {soldOutPoints.map((point, index) => (
              <ReferenceDot
                key={`soldout-${index}`}
                yAxisId="right"
                x={point.date}
                y={point.bookings}
                r={6}
                fill="#f43f5e"
                stroke="#ffffff"
                strokeWidth={2}
                label={{ value: 'Sold Out', fill: '#f43f5e', position: 'top', fontSize: 10 }}
              />
            ))}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
