import React from 'react';
import { render, screen } from '@testing-library/react';
import ForecastChart from '../components/ForecastChart';

describe('ForecastChart Component', () => {
  test('renders ForecastChart with confidence intervals and P50 line when data is provided', () => {
    const mockForecast = [
      { date: '2026-03-01', item_id: 'ITM-001', p10: 5, p50: 10, p90: 15 },
      { date: '2026-03-02', item_id: 'ITM-001', p10: 6, p50: 12, p90: 18 }
    ];

    render(<ForecastChart data={mockForecast} selectedItemName="Eiffel Tower Tour" />);

    expect(screen.getByText(/90-Day Demand Forecast \(P50 & P10-P90 Band\) - Eiffel Tower Tour/i)).toBeInTheDocument();
    expect(screen.getByText('P10 - P90 Confidence Band')).toBeInTheDocument();
    expect(screen.getByText('P50 Expected Demand')).toBeInTheDocument();
  });

  test('renders empty message when no forecast data is provided', () => {
    render(<ForecastChart data={[]} />);

    expect(screen.getByText(/No 90-day forecast data available for the selected item./i)).toBeInTheDocument();
  });
});
