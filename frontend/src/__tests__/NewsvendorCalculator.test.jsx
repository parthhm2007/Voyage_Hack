import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import NewsvendorCalculator from '../components/NewsvendorCalculator';
import * as api from '../services/api';

vi.mock('../services/api', () => ({
  getNewsvendor: vi.fn(),
}));

describe('NewsvendorCalculator Component', () => {
  const mockItem = {
    item_id: 'H001',
    item_type: 'hotel',
    destination: 'Goa',
    name: 'Azure Coast Budget Inn',
    base_supplier_cost: 1644.0,
    base_sell_price: 2135.55
  };

  test('renders NewsvendorCalculator inputs and fetches optimization on load', async () => {
    api.getNewsvendor.mockResolvedValueOnce({
      item_id: 'H001',
      item_name: 'Azure Coast Budget Inn',
      item_type: 'hotel',
      capacity_per_day: 99,
      capacity_capped: true,
      unit_cost: 1644.0,
      sell_price: 2135.55,
      salvage_value: 657.6,
      critical_fractile: 0.3542,
      optimal_quantity_avg: 45.5,
      total_optimal_quantity: 455.0,
      total_expected_profit: 12500.0,
      expected_demand_avg: 50.0,
      assumptions: {
        salvage_rate: 0.40,
        salvage_value: 657.6,
        capacity_per_day: 99
      },
      daily_breakdown: [
        { date: '2026-03-01', p10: 30, p50: 50, p90: 70, expected_demand: 50, optimal_quantity: 45, expected_profit: 1250 }
      ]
    });

    render(<NewsvendorCalculator itemId="H001" itemObj={mockItem} />);

    expect(screen.getByText(/Newsvendor Inventory Optimization/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Unit Cost/i)).toHaveValue(1644);
    expect(screen.getByLabelText(/Sell Price/i)).toHaveValue(2135.55);

    await waitFor(() => {
      expect(screen.getByText('45.5')).toBeInTheDocument();
      expect(screen.getByText('₹12,500')).toBeInTheDocument();
      expect(screen.getByText(/Assumptions: Salvage rate 40%/i)).toBeInTheDocument();
      expect(screen.getAllByText(/Quantity capped at physical capacity/i).length).toBeGreaterThan(0);
    });
  });
});
