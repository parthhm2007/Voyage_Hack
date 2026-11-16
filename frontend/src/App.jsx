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
  const [historyError, setHistoryError] = useState(null);

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
        // Default load: select the first available item automatically (F4)
        if (itemsData && itemsData.length > 0) {
          setSelectedItemId(itemsData[0].item_id);
        }
      } catch (err) {
        console.error('Failed to load initial data:', err);
        setError('Failed to connect to backend server. Please ensure FastAPI is running.');
      } finally {
        setLoading(false);
      }
    };
    loadInitialData();
  }, []);

  // Function to load history data
  const loadHistoryData = async () => {
    try {
      setHistoryLoading(true);
      setHistoryError(null);
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
      // Visible history fetch error banner state (F10)
      setHistoryError('Failed to load historical booking records from backend. Please check backend connection.');
    } finally {
      setHistoryLoading(false);
    }
  };

  // Load history whenever filters change
  useEffect(() => {
    if (selectedItemId || (selectedDestination && selectedDestination !== 'All')) {
      loadHistoryData();
    }
  }, [selectedDestination, selectedItemId]);

  const handleReset = () => {
    setSelectedDestination('All');
    if (items && items.length > 0) {
      setSelectedItemId(items[0].item_id);
    } else {
      setSelectedItemId('');
    }
  };

  return (
    <div className="app-container">
      {/* Navbar (F3: Responsive stack below 640px) */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-brand">
            <div className="header-icon-badge">
              <Compass size={24} />
            </div>
            <div className="header-title-group">
              <h1>TBO Inventory Data Explorer</h1>
              <p>Phase 1: Demand & Capacity Baseline</p>
            </div>
          </div>
          <div>
            <span className="header-status-badge">
              Live Backend Connected
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        {error ? (
          <div className="alert-banner">
            <div>
              <h3 className="alert-title">Connection Error</h3>
              <p className="alert-message">{error}</p>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="alert-retry-btn"
              type="button"
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

            {/* History Fetch Error Banner with Retry (F10) */}
            {historyError && (
              <div className="alert-banner">
                <div>
                  <h3 className="alert-title">Data Loading Warning</h3>
                  <p className="alert-message">{historyError}</p>
                </div>
                <button
                  onClick={loadHistoryData}
                  className="alert-retry-btn"
                  type="button"
                >
                  Retry
                </button>
              </div>
            )}

            {/* Charts & Visualizations */}
            {historyLoading ? (
              <div className="loading-box">
                <RefreshCw size={24} className="spin-icon" />
                <span>Loading history data...</span>
              </div>
            ) : (
              <BookingsChart data={history} />
            )}

            {/* Recent History Table Preview */}
            <div className="table-card">
              <div className="table-header-bar">
                <h3 className="table-title">Historical Records Overview</h3>
                <span className="table-count-label">Showing {history.length} records</span>
              </div>
              <div className="table-scroll">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Item ID</th>
                      <th>Searches</th>
                      <th>Bookings</th>
                      <th>Sold Out</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.slice(0, 50).map((row, idx) => (
                      <tr key={idx}>
                        <td>{row.date}</td>
                        <td className="code-cell">{row.item_id}</td>
                        <td>{row.searches?.toLocaleString()}</td>
                        <td>{row.bookings?.toLocaleString()}</td>
                        <td>
                          {row.sold_out_flag === 1 ? (
                            <span className="sold-out-badge">
                              Sold Out
                            </span>
                          ) : (
                            <span className="empty-cell">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                    {history.length === 0 && (
                      <tr>
                        <td colSpan="5" className="table-empty-message">
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
