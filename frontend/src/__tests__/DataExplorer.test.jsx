import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SummaryCards from '../components/SummaryCards';
import FilterBar from '../components/FilterBar';
import BookingsChart, { aggregateHistoryByDate } from '../components/BookingsChart';

describe('Data Explorer Components', () => {
  test('SummaryCards renders metrics correctly', () => {
    const summary = {
      total_items: 120,
      total_bookings: 540,
      total_searches: 2300,
      total_sold_out_days: 15,
      destinations: ['Paris', 'Tokyo']
    };

    render(<SummaryCards summary={summary} />);

    expect(screen.getByText('Total Inventory Items')).toBeInTheDocument();
    expect(screen.getByText('120')).toBeInTheDocument();
    expect(screen.getByText('Total Bookings')).toBeInTheDocument();
    expect(screen.getByText('540')).toBeInTheDocument();
    expect(screen.getByText('Total Searches')).toBeInTheDocument();
    expect(screen.getByText('2,300')).toBeInTheDocument();
    expect(screen.getByText('Sold-Out Days')).toBeInTheDocument();
    expect(screen.getByText('15')).toBeInTheDocument();
  });

  test('FilterBar renders options and handles selection', () => {
    const destinations = ['Paris', 'Tokyo'];
    const items = [
      { item_id: 'ITM-001', item_name: 'Eiffel Tower Tour', destination: 'Paris' },
      { item_id: 'ITM-002', item_name: 'Tokyo Skytree', destination: 'Tokyo' }
    ];

    const setSelectedDestination = vi.fn();
    const setSelectedItemId = vi.fn();
    const onReset = vi.fn();

    render(
      <FilterBar
        destinations={destinations}
        items={items}
        selectedDestination="Paris"
        setSelectedDestination={setSelectedDestination}
        selectedItemId="ITM-001"
        setSelectedItemId={setSelectedItemId}
        onReset={onReset}
      />
    );

    expect(screen.getByText('Filters:')).toBeInTheDocument();
    expect(screen.getByText('Paris')).toBeInTheDocument();
    expect(screen.getByText('Eiffel Tower Tour (ITM-001)')).toBeInTheDocument();

    const resetButton = screen.getByText('Reset');
    fireEvent.click(resetButton);
    expect(onReset).toHaveBeenCalled();
  });

  test('BookingsChart renders chart container and legend when data is present', () => {
    const historyData = [
      { date: '2026-01-01', searches: 50, bookings: 10, sold_out_flag: 0 },
      { date: '2026-01-02', searches: 120, bookings: 25, sold_out_flag: 1 }
    ];

    render(<BookingsChart data={historyData} />);

    expect(screen.getByText('Bookings vs Searches Over Time')).toBeInTheDocument();
    expect(screen.getByText('Searches')).toBeInTheDocument();
    expect(screen.getByText('Bookings')).toBeInTheDocument();
    expect(screen.getByText('Sold Out Day')).toBeInTheDocument();
  });

  test('aggregateHistoryByDate properly aggregates multi-item records by date', () => {
    const rawMultiItemData = [
      { date: '2026-01-01', item_id: 'ITM-001', searches: 100, bookings: 10, sold_out_flag: 0 },
      { date: '2026-01-01', item_id: 'ITM-002', searches: 150, bookings: 20, sold_out_flag: 1 },
      { date: '2026-01-02', item_id: 'ITM-001', searches: 80, bookings: 5, sold_out_flag: 0 },
      { date: '2026-01-02', item_id: 'ITM-002', searches: 90, bookings: 15, sold_out_flag: 0 },
    ];

    const aggregated = aggregateHistoryByDate(rawMultiItemData);
    expect(aggregated).toHaveLength(2);
    expect(aggregated[0]).toEqual({
      date: '2026-01-01',
      searches: 250,
      bookings: 30,
      sold_out_flag: 1,
    });
    expect(aggregated[1]).toEqual({
      date: '2026-01-02',
      searches: 170,
      bookings: 20,
      sold_out_flag: 0,
    });
  });
});
