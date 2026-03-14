import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Refund endpoints
export const submitRefund = (data) => api.post('/refund', data);
export const getRefund = (id) => api.get(`/refund/${id}`);
export const listRefunds = (limit = 50) => api.get(`/refund?limit=${limit}`);

// Dashboard endpoints
export const getDashboardStats = () => api.get('/dashboard/stats');
export const getRecentRefunds = (limit = 20) => api.get(`/dashboard/refunds?limit=${limit}`);
export const getCustomers = () => api.get('/dashboard/customers');
export const getCustomerDetail = (id) => api.get(`/dashboard/customers/${id}`);

// NL Query
export const merchantQuery = (query) => api.post('/query', { query });

// Evidence upload
export const uploadEvidence = (refundId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/webhook/evidence/${refundId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export default api;
