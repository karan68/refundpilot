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
export const getAlerts = () => api.get('/dashboard/alerts');
export const getAuditLog = (limit = 50) => api.get(`/dashboard/audit-log?limit=${limit}`);
export const getReconciliation = () => api.get('/dashboard/reconciliation');
export const getFraudGraph = () => api.get('/dashboard/fraud-graph');
export const getFraudSimilarity = (id) => api.get(`/dashboard/fraud-similarity/${id}`);

// Cohort endpoints
export const getProductCohorts = () => api.get('/dashboard/cohorts/products');
export const getCityCohorts = () => api.get('/dashboard/cohorts/cities');
export const getReasonCohorts = () => api.get('/dashboard/cohorts/reasons');

// NL Query
export const merchantQuery = (query) => api.post('/query', { query });

// F25: Conversational refund
export const chatRefund = (message, language = 'en') => api.post('/chat/refund', { message, language });

// Evidence upload
export const uploadEvidence = (refundId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/webhook/evidence/${refundId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Fraud ring check
export const checkFraudRing = (refundId) => api.post(`/webhook/fraud-ring/${refundId}`);

export default api;
