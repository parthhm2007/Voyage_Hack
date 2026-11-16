import React from 'react';
import { Package, CalendarCheck, Search, AlertCircle } from 'lucide-react';

export default function SummaryCards({ summary }) {
  if (!summary) {
    return (
      <div className="kpi-grid">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="kpi-skeleton">
            <div className="skeleton-line skeleton-title"></div>
            <div className="skeleton-line skeleton-value"></div>
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
      colorClass: 'kpi-blue',
    },
    {
      title: 'Total Bookings',
      value: summary.total_bookings?.toLocaleString() || '0',
      icon: CalendarCheck,
      colorClass: 'kpi-emerald',
    },
    {
      title: 'Total Searches',
      value: summary.total_searches?.toLocaleString() || '0',
      icon: Search,
      colorClass: 'kpi-indigo',
    },
    {
      title: 'Sold-Out Days',
      value: summary.total_sold_out_days?.toLocaleString() || '0',
      icon: AlertCircle,
      colorClass: 'kpi-rose',
    },
  ];

  return (
    <div className="kpi-grid">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div key={idx} className="kpi-card">
            <div>
              <p className="kpi-title">{card.title}</p>
              <p className="kpi-value">{card.value}</p>
            </div>
            <div className={`kpi-icon-wrapper ${card.colorClass}`}>
              <Icon size={24} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
