import client from './client'

export const getDrivers = (params = {}) =>
  client.get('/api/drivers/', { params }).then((r) => r.data)

export const getDriver = (id) =>
  client.get(`/api/drivers/${id}`).then((r) => r.data)

export const createDriver = (data) =>
  client.post('/api/drivers/', data).then((r) => r.data)

export const updateDriver = (id, data) =>
  client.put(`/api/drivers/${id}`, data).then((r) => r.data)

export const deleteDriver = (id) =>
  client.delete(`/api/drivers/${id}`)
