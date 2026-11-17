import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import RecommendationsTable from '../components/RecommendationsTable';
import * as api from '../services/api';

vi.mock('../services/api', () => ({
  getOptimization: vi.fn(),
}));

describe('RecommendationsTable Component', () => {
  test('renders RecommendationsTable, risk slider, and portfolio recommendations on load', async () => {
    api.getOptimization.mockResolvedValueOnce({
      total_budget: 500000.0,
      risk_appetite: 0.5,
      allocated_budget: 490000.0,
      total_expected_profit: 160000.0,
      portfolio_roi: 0.3265,
      allocations: [
        {
          item_id: 'H002',
          item_name: 'Hilltop Grand Resort',
          item_type: 'hotel',
          destination: 'Shimla',
          allocated_budget: 150000.0,
          units_purchased: 90.0,
          expected_profit: 55000.0,
          roi: 0.3667
        }
      ]
    });

    render(<RecommendationsTable />);

    expect(screen.getByText(/Portfolio Recommendations Table/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Total Capital Budget/i)).toHaveValue(500000);
    expect(screen.getByLabelText(/Risk Appetite/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Hilltop Grand Resort')).toBeInTheDocument();
      expect(screen.getByText(/Expected Portfolio Profit/i)).toBeInTheDocument();
    });
  });
});
