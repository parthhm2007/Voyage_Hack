import React, { useState, useEffect } from 'react';
import { fetchSummary, fetchItems, fetchHistory } from './services/api';
import SummaryCards from './components/SummaryCards';
import FilterBar from './components/FilterBar';
import BookingsChart from './components/BookingsChart';
import { Compass, RefreshCw } from 'lucide-react';

export default function App() {
  const [summary, setSummary] = useState(null);
  const [items, setItems] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedDestination, setSelectedDestination] = useState('All');
  const [selectedItemId, setSelectedItemId] = useState('');
  const [loading, setLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load initial summary and items
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        const [summaryData, itemsData] = await Promise.all([
          fetchSummary(),
          fetchItems(),
        ]);
        setSummary(summaryData);
        setItems(itemsData);
      } catch (err) {
        console.error('Failed to load initial data:', err);
        setError('Failed to connect to backend server. Please ensure FastAPI is running.');
      } finally {
        setLoading(false);
      }
    };
    loadInitialData();
  }, []);

  // Load history whenever filters change
  useEffect(() => {
    const loadHistoryData = async () => {
      try {
        setHistoryLoading(true);
        const params = {};
        if (selectedDestination && selectedDestination !== 'All') {
          params.destination = selectedDestination;
        }
        if (selectedItemId) {
          params.item_id = selectedItemId;
        }
        params.limit = 500; // Limit for performance
        const historyData = await fetchHistory(params);
        setHistory(historyData);
      } catch (err) {
        console.error('Failed to load history data:', err);
      } finally {
        setHistoryLoading(false);
      }
    };
    loadHistoryData();
  }, [selectedDestination, selectedItemId]);

  const handleReset = () => {
    setSelectedDestination('All');
    setSelectedItemId('');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Navbar */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-2 rounded-xl text-white shadow-sm">
              <Compass className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 tracking-tight">TBO Inventory Data Explorer</h1>
              <p className="text-xs text-gray-500">Phase 1: Demand & Capacity Baseline</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
              Live Backend Connected
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error ? (
          <div className="bg-rose-50 border border-rose-200 text-rose-700 p-6 rounded-xl shadow-sm mb-6 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Connection Error</h3>
              <p className="text-sm mt-1">{error}</p>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-rose-600 text-white text-sm font-medium rounded-lg hover:bg-rose-700 transition-colors"
            >
              Retry
            </button>
          </div>
        ) : (
          <>
            {/* Summary KPI Cards */}
            <SummaryCards summary={summary} />

            {/* Filter Bar */}
            <FilterBar
              destinations={summary?.destinations || []}
              items={items}
              selectedDestination={selectedDestination}
              setSelectedDestination={setSelectedDestination}
              selectedItemId={selectedItemId}
              setSelectedItemId={setSelectedItemId}
              onReset={handleReset}
            />

            {/* Charts & Visualizations */}
            {historyLoading ? (
              <div className="bg-white p-12 rounded-xl shadow-sm border border-gray-100 flex items-center justify-center mb-6">
                <RefreshCw className="w-6 h-6 animate-spin text-blue-600 mr-2" />
                <span className="text-gray-600 font-medium">Loading history data...</span>
              </div>
            ) : (
              <BookingsChart data={history} />
            )}

            {/* Recent History Table Preview */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-800">Historical Records Overview</h3>
                <span className="text-xs text-gray-500">Showing {history.length} records</span>
              </div>
              <div className="overflow-x-auto max-h-96">
                <table className="w-full text-left border-collapse">
                  <thead className="bg-gray-50 sticky top-0 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    <tr>
                      <th className="px-6 py-3">Date</th>
                      <th className="px-6 py-3">Item ID</th>
                      <th className="px-6 py-3">Searches</th>
                      <th className="px-6 py-3">Bookings</th>
                      <th className="px-6 py-3">Sold Out</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 text-sm text-gray-700">
                    {history.slice(0, 50).map((row, idx) => (
                      <tr key={idx} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-3 font-medium">{row.date}</td>
                        <td className="px-6 py-3 font-mono text-xs text-gray-500">{row.item_id}</td>
                        <td className="px-6 py-3">{row.searches}</td>
                        <td className="px-6 py-3">{row.bookings}</td>
                        <td className="px-6 py-3">
                          {row.sold_out_flag === 1 ? (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-rose-100 text-rose-800">
                              Sold Out
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                    {history.length === 0 && (
                      <tr>
                        <td colSpan="5" className="px-6 py-8 text-center text-gray-400">
                          No records found.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
