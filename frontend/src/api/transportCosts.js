import client from './client'

export const getTransportCosts = (params = {}) =>
  client.get('/api/transport-costs/', { params }).then((r) => r.data)

export const getTransportCost = (id) =>
  client.get(`/api/transport-costs/${id}`).then((r) => r.data)

export const createTransportCost = (data) =>
  client.post('/api/transport-costs/', data).then((r) => r.data)

export const updateTransportCost = (id, data) =>
  client.put(`/api/transport-costs/${id}`, data).then((r) => r.data)

export const deleteTransportCost = (id) =>
  client.delete(`/api/transport-costs/${id}`)
