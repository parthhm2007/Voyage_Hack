import React, { useState, useEffect } from 'react';
import { fetchSummary, fetchItems, fetchHistory, getForecast } from './services/api';
import SummaryCards from './components/SummaryCards';
import FilterBar from './components/FilterBar';
import BookingsChart from './components/BookingsChart';
import ForecastChart from './components/ForecastChart';
import { Compass, RefreshCw } from 'lucide-react';

export default function App() {
  const [summary, setSummary] = useState(null);
  const [items, setItems] = useState([]);
  const [history, setHistory] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [selectedDestination, setSelectedDestination] = useState('All');
  const [selectedItemId, setSelectedItemId] = useState('');
  const [loading, setLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [error, setError] = useState(null);
  const [historyError, setHistoryError] = useState(null);
  const [forecastError, setForecastError] = useState(null);

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
        // Default load: select the first available item automatically
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
      setHistoryError('Failed to load historical booking records from backend. Please check backend connection.');
    } finally {
      setHistoryLoading(false);
    }
  };

  // Function to load 90-day forecast data
  const loadForecastData = async () => {
    if (!selectedItemId) {
      setForecast([]);
      return;
    }
    try {
      setForecastLoading(true);
      setForecastError(null);
      const forecastData = await getForecast(selectedItemId);
      setForecast(forecastData);
    } catch (err) {
      console.error('Failed to load forecast data:', err);
      setForecastError('Failed to load 90-day forecast from backend. Please check backend connection.');
    } finally {
      setForecastLoading(false);
    }
  };

  // Load history and forecast whenever filters change
  useEffect(() => {
    if (selectedItemId || (selectedDestination && selectedDestination !== 'All')) {
      loadHistoryData();
      if (selectedItemId) {
        loadForecastData();
      } else {
        setForecast([]);
      }
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

  const selectedItemObj = items.find(i => i.item_id === selectedItemId);
  const selectedItemName = selectedItemObj ? (selectedItemObj.item_name || selectedItemObj.item_id) : selectedItemId;

  return (
    <div className="app-container">
      {/* Navbar */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-brand">
            <div className="header-icon-badge">
              <Compass size={24} />
            </div>
            <div className="header-title-group">
              <h1>TBO Inventory Data Explorer & Forecast</h1>
              <p>Phase 3: XGBoost Demand Forecasting & Confidence Bands</p>
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

            {/* History Fetch Error Banner with Retry */}
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

            {/* Forecast Fetch Error Banner with Retry */}
            {forecastError && (
              <div className="alert-banner">
                <div>
                  <h3 className="alert-title">Forecast Loading Warning</h3>
                  <p className="alert-message">{forecastError}</p>
                </div>
                <button
                  onClick={loadForecastData}
                  className="alert-retry-btn"
                  type="button"
                >
                  Retry
                </button>
              </div>
            )}

            {/* 90-Day Forecast Chart */}
            {forecastLoading ? (
              <div className="loading-box">
                <RefreshCw size={24} className="spin-icon" />
                <span>Loading 90-day forecast data...</span>
              </div>
            ) : (
              <ForecastChart data={forecast} selectedItemName={selectedItemName} />
            )}

            {/* Historical Bookings vs Searches Chart */}
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
