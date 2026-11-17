import axios from 'axios';

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchSummary = async () => {
  const response = await api.get('/api/summary');
  return response.data;
};

export const fetchItems = async (params = {}) => {
  const response = await api.get('/api/items', { params });
  return response.data;
};

export const fetchCalendar = async (params = {}) => {
  const response = await api.get('/api/calendar', { params });
  return response.data;
};

export const fetchHistory = async (params = {}) => {
  const response = await api.get('/api/history', { params });
  return response.data;
};

export const getForecast = async (itemId) => {
  const response = await api.get('/api/forecast', { params: { item_id: itemId } });
  return response.data;
};

export const getNewsvendor = async (itemId, params = {}) => {
  const response = await api.get('/api/newsvendor', { params: { item_id: itemId, ...params } });
  return response.data;
};

export const getOptimization = async (totalBudget, riskAppetite = 0.5, params = {}) => {
  const response = await api.get('/api/optimize', { 
    params: { total_budget: totalBudget, risk_appetite: riskAppetite, ...params } 
  });
  return response.data;
};

export default api;
