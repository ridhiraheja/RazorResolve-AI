import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

export default api

// Typed helpers
export const getDashboardOverview = () => api.get('/dashboard/overview')
export const getRevenueTrend = (days = 30) => api.get(`/dashboard/revenue-trend?days=${days}`)
export const getFailureBreakdown = () => api.get('/dashboard/failure-breakdown')

export const getIncidents = (params?: Record<string, string>) =>
  api.get('/incidents', { params })
export const getIncident = (id: string) => api.get(`/incidents/${id}`)
export const updateIncidentStatus = (id: string, status: string) =>
  api.patch(`/incidents/${id}/status`, { status })
export const approveIncident = (id: string) => api.post(`/incidents/${id}/approve`)
export const rejectIncident = (id: string) => api.post(`/incidents/${id}/reject`)

export const getPayments = (params?: Record<string, string>) =>
  api.get('/payments', { params })
export const getPayment = (id: string) => api.get(`/payments/${id}`)

export const getProducts = (params?: Record<string, string>) =>
  api.get('/products', { params })
export const getProduct = (id: string) => api.get(`/products/${id}`)
export const getRecommendations = (query: string, limit = 5) =>
  api.post('/products/recommend', { query, limit })

export const getCarts = (params?: Record<string, string>) =>
  api.get('/carts', { params })

export const getAuditLogs = (params?: Record<string, string>) =>
  api.get('/audit/logs', { params })
export const getAIDecisions = (incidentId?: string) =>
  api.get('/audit/decisions', { params: incidentId ? { incident_id: incidentId } : {} })

export const sendFinancialChat = (message: string) =>
  api.post('/financial/chat', { message })
