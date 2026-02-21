import client from './client'

export const getPayments = (params = {}) =>
  client.get('/api/payments/', { params }).then((r) => r.data)

export const getPayment = (id) =>
  client.get(`/api/payments/${id}`).then((r) => r.data)

export const createPayment = (data) =>
  client.post('/api/payments/', data).then((r) => r.data)

export const updatePayment = (id, data) =>
  client.put(`/api/payments/${id}`, data).then((r) => r.data)

export const deletePayment = (id) =>
  client.delete(`/api/payments/${id}`)
