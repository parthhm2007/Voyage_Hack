import '@testing-library/jest-dom';

// Mock ResizeObserver for Recharts ResponsiveContainer in test environment
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserver;
global.ResizeObserver = ResizeObserver;
