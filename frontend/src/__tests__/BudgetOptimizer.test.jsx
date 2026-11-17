import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import BudgetOptimizer from '../components/BudgetOptimizer';
import * as api from '../services/api';

vi.mock('../services/api', () => ({
  getOptimization: vi.fn(),
}));

describe('BudgetOptimizer Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders BudgetOptimizer and displays optimization allocations in rupees (₹) on load', async () => {
    api.getOptimization.mockResolvedValueOnce({
      total_budget: 500000.0,
      allocated_budget: 485000.0,
      total_expected_profit: 150000.0,
      portfolio_roi: 0.3093,
      allocations: [
        {
          item_id: 'H001',
          item_name: 'Azure Coast Budget Inn',
          item_type: 'hotel',
          destination: 'Goa',
          allocated_budget: 120000.0,
          units_purchased: 75,
          expected_profit: 45000.0,
          roi: 0.375
        }
      ]
    });

    render(<BudgetOptimizer />);

    expect(screen.getByText(/Portfolio Budget Optimizer/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Total Capital Budget \(₹\)/i)).toHaveValue(500000);

    await waitFor(() => {
      expect(screen.getByText('Azure Coast Budget Inn')).toBeInTheDocument();
      expect(screen.getByText(/Expected Portfolio Profit/i)).toBeInTheDocument();
      expect(screen.getByText('₹4,85,000')).toBeInTheDocument();
      expect(screen.getByText('₹1,50,000')).toBeInTheDocument();
    });
  });
});
