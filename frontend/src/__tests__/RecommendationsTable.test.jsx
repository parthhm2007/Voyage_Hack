import React from 'react';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import RecommendationsTable, { formatRupee, formatNumber, formatPercent } from '../components/RecommendationsTable';
import * as api from '../services/api';

vi.mock('../services/api', () => ({
  getOptimization: vi.fn(),
}));

describe('RecommendationsTable Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('formatting helpers format correctly and return em-dash on null/undefined/NaN', () => {
    expect(formatRupee(null)).toBe('—');
    expect(formatRupee(undefined)).toBe('—');
    expect(formatRupee(NaN)).toBe('—');
    expect(formatRupee(1000000)).toBe('₹10,00,000');

    expect(formatNumber(null)).toBe('—');
    expect(formatNumber(undefined)).toBe('—');
    expect(formatNumber(5000)).toBe('5,000');

    expect(formatPercent(null)).toBe('—');
    expect(formatPercent(undefined)).toBe('—');
    expect(formatPercent(0.355)).toBe('35.5%');
  });

  test('renders RecommendationsTable, risk slider, and rupee symbols (₹) on load', async () => {
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
          unit_cost: 5000.0,
          allocated_budget: 150000.0,
          units_purchased: 30,
          expected_profit: 55000.0,
          roi: 0.3667,
          capacity_per_day: 50,
          capacity_capped: false
        }
      ],
      assumptions: {
        salvage_rates: { hotel: 0.4, flight: 0.15 },
        risk_weights: { p10: 0.25, p50: 0.5, p90: 0.25 },
        start_date: '2026-11-15',
        end_date: '2027-02-12',
        days: 90
      }
    });

    render(<RecommendationsTable />);

    expect(screen.getByText(/Portfolio Recommendations Table/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Total Capital Budget \(₹\)/i)).toHaveValue(500000);
    expect(screen.getByLabelText(/Risk Appetite/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Hilltop Grand Resort')).toBeInTheDocument();
      expect(screen.getByText(/Expected Portfolio Profit/i)).toBeInTheDocument();
      // Rupee symbol in KPIs and summary
      expect(screen.getAllByText('₹4,90,000').length).toBeGreaterThan(0);
      expect(screen.getAllByText('₹1,60,000').length).toBeGreaterThan(0);
    });
  });

  test('handles null and undefined fields gracefully without displaying NaN or undefined', async () => {
    api.getOptimization.mockResolvedValueOnce({
      total_budget: 500000.0,
      risk_appetite: 0.5,
      allocated_budget: null,
      total_expected_profit: undefined,
      portfolio_roi: NaN,
      allocations: [
        {
          item_id: 'H003',
          item_name: 'Desert Mirage Oasis',
          item_type: 'hotel',
          destination: 'Jaisalmer',
          unit_cost: null,
          allocated_budget: undefined,
          units_purchased: null,
          expected_profit: NaN,
          roi: undefined
        }
      ]
    });

    render(<RecommendationsTable />);

    await waitFor(() => {
      expect(screen.getByText('Desert Mirage Oasis')).toBeInTheDocument();
    });

    // None of "NaN", "undefined", or "null" should be displayed as exact values
    expect(screen.queryByText('NaN')).not.toBeInTheDocument();
    expect(screen.queryByText('undefined')).not.toBeInTheDocument();
    expect(screen.queryByText('null')).not.toBeInTheDocument();
  });

  test('does not call API on invalid budget input and shows validation message', async () => {
    render(<RecommendationsTable />);

    const input = screen.getByLabelText(/Total Capital Budget \(₹\)/i);

    // Empty budget
    fireEvent.change(input, { target: { value: '' } });
    await waitFor(() => {
      expect(screen.getAllByText(/Please enter a total capital budget/i).length).toBeGreaterThan(0);
    });

    // Negative budget
    fireEvent.change(input, { target: { value: '-500' } });
    await waitFor(() => {
      expect(screen.getAllByText(/Budget cannot be negative/i).length).toBeGreaterThan(0);
    });

    // Exceeding MAX_BUDGET
    fireEvent.change(input, { target: { value: '2000000000' } });
    await waitFor(() => {
      expect(screen.getAllByText(/Budget cannot exceed/i).length).toBeGreaterThan(0);
    });
  });

  test('error state clears previous result and shows working Retry button', async () => {
    api.getOptimization.mockRejectedValueOnce(new Error('Network error'));

    render(<RecommendationsTable />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to compute portfolio recommendations from backend/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Retry/i })).toBeInTheDocument();
    });

    // Mock successful retry
    api.getOptimization.mockResolvedValueOnce({
      total_budget: 500000.0,
      risk_appetite: 0.5,
      allocated_budget: 250000.0,
      total_expected_profit: 80000.0,
      portfolio_roi: 0.32,
      allocations: []
    });

    const retryBtn = screen.getByRole('button', { name: /Retry/i });
    fireEvent.click(retryBtn);

    await waitFor(() => {
      expect(screen.queryByText(/Failed to compute portfolio recommendations/i)).not.toBeInTheDocument();
      expect(screen.getAllByText('₹2,50,000').length).toBeGreaterThan(0);
    });
  });

  test('stale slower response does not overwrite newer response', async () => {
    vi.useFakeTimers();

    let resolveFirst;
    let resolveSecond;

    api.getOptimization.mockImplementation((budget) => {
      if (budget === 500000) {
        return new Promise((resolve) => {
          resolveFirst = () => resolve({
            total_budget: 500000,
            risk_appetite: 0.5,
            allocated_budget: 450000,
            total_expected_profit: 100000,
            portfolio_roi: 0.22,
            allocations: [{ item_id: 'OLD', item_name: 'Old Hotel', allocated_budget: 450000 }]
          });
        });
      }
      return new Promise((resolve) => {
        resolveSecond = () => resolve({
          total_budget: 1000000,
          risk_appetite: 0.5,
          allocated_budget: 950000,
          total_expected_profit: 300000,
          portfolio_roi: 0.31,
          allocations: [{ item_id: 'NEW', item_name: 'New Hotel', allocated_budget: 950000 }]
        });
      });
    });

    render(<RecommendationsTable />);

    // Advance to trigger first call
    act(() => {
      vi.advanceTimersByTime(350);
    });

    // Change budget to 1,000,000
    const input = screen.getByLabelText(/Total Capital Budget \(₹\)/i);
    fireEvent.change(input, { target: { value: '1000000' } });

    // Advance to trigger second call
    act(() => {
      vi.advanceTimersByTime(350);
    });

    // Resolve second request first
    await act(async () => {
      resolveSecond();
    });

    // Now resolve first (stale) request later
    await act(async () => {
      resolveFirst();
    });

    // Document should show results of the newer request (New Hotel), not Old Hotel
    expect(screen.getByText('New Hotel')).toBeInTheDocument();
    expect(screen.queryByText('Old Hotel')).not.toBeInTheDocument();

    vi.useRealTimers();
  });
});
