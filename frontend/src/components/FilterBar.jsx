import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';

export default function FilterBar({
  destinations = [],
  items = [],
  selectedDestination,
  setSelectedDestination,
  selectedItemId,
  setSelectedItemId,
  onReset,
}) {
  // Filter items based on selected destination if any
  const filteredItems = selectedDestination && selectedDestination !== 'All'
    ? items.filter(item => item.destination === selectedDestination)
    : items;

  return (
    <div className="filter-bar">
      <div className="filter-controls-group">
        <div className="filter-label-header">
          <Filter size={18} />
          <span>Filters:</span>
        </div>

        {/* Destination Filter */}
        <div className="filter-item">
          <label htmlFor="destination-select" className="filter-item-label">Destination</label>
          <select
            id="destination-select"
            value={selectedDestination || 'All'}
            onChange={(e) => {
              const newDest = e.target.value;
              setSelectedDestination(newDest);
              // Auto-select the first item matching the new destination (F4)
              const matchingItems = newDest && newDest !== 'All'
                ? items.filter(item => item.destination === newDest)
                : items;
              if (matchingItems.length > 0) {
                setSelectedItemId(matchingItems[0].item_id);
              } else {
                setSelectedItemId('');
              }
            }}
            className="filter-select"
          >
            <option value="All">All Destinations</option>
            {destinations.map((dest) => (
              <option key={dest} value={dest}>
                {dest}
              </option>
            ))}
          </select>
        </div>

        {/* Item Filter (F4: "All items" option removed as multi-item exceeds 10,000 limit) */}
        <div className="filter-item">
          <label htmlFor="item-select" className="filter-item-label">Item</label>
          <select
            id="item-select"
            value={selectedItemId || ''}
            onChange={(e) => setSelectedItemId(e.target.value)}
            className="filter-select filter-select-wide"
          >
            {filteredItems.map((item) => (
              <option key={item.item_id} value={item.item_id}>
                {item.item_name} ({item.item_id})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Reset button */}
      <div>
        <button
          onClick={onReset}
          className="btn-reset"
          type="button"
        >
          <RotateCcw size={16} />
          <span>Reset</span>
        </button>
      </div>
    </div>
  );
}
