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

export default api;
