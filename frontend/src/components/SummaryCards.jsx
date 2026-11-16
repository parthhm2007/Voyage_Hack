import React from 'react';
import { Package, CalendarCheck, Search, AlertCircle } from 'lucide-react';

export default function SummaryCards({ summary }) {
  if (!summary) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: 'Total Inventory Items',
      value: summary.total_items?.toLocaleString() || '0',
      icon: Package,
      color: 'bg-blue-50 text-blue-600',
    },
    {
      title: 'Total Bookings',
      value: summary.total_bookings?.toLocaleString() || '0',
      icon: CalendarCheck,
      color: 'bg-emerald-50 text-emerald-600',
    },
    {
      title: 'Total Searches',
      value: summary.total_searches?.toLocaleString() || '0',
      icon: Search,
      color: 'bg-indigo-50 text-indigo-600',
    },
    {
      title: 'Sold-Out Days',
      value: summary.total_sold_out_days?.toLocaleString() || '0',
      icon: AlertCircle,
      color: 'bg-rose-50 text-rose-600',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div key={idx} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">{card.title}</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{card.value}</p>
            </div>
            <div className={`p-3 rounded-xl ${card.color}`}>
              <Icon className="w-6 h-6" />
            </div>
          </div>
        );
      })}
    </div>
  );
}
