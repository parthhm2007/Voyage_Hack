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
    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 mb-6 flex flex-wrap items-center justify-between gap-4">
      <div className="flex flex-wrap items-center gap-4 flex-1">
        <div className="flex items-center space-x-2 text-gray-700 font-medium">
          <Filter className="w-5 h-5 text-gray-400" />
          <span>Filters:</span>
        </div>

        {/* Destination Filter */}
        <div className="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-2">
          <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Destination</label>
          <select
            value={selectedDestination || 'All'}
            onChange={(e) => {
              setSelectedDestination(e.target.value);
              setSelectedItemId(''); // Reset item when destination changes
            }}
            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2"
          >
            <option value="All">All Destinations</option>
            {destinations.map((dest) => (
              <option key={dest} value={dest}>
                {dest}
              </option>
            ))}
          </select>
        </div>

        {/* Item Filter */}
        <div className="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-2">
          <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Item</label>
          <select
            value={selectedItemId || ''}
            onChange={(e) => setSelectedItemId(e.target.value)}
            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2 max-w-xs"
          >
            <option value="">All Items ({filteredItems.length})</option>
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
          className="inline-flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Reset</span>
        </button>
      </div>
    </div>
  );
}
