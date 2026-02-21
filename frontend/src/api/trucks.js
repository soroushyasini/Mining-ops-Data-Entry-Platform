import client from './client'

export const getTrucks = (params = {}) =>
  client.get('/api/trucks/', { params }).then((r) => r.data)

export const getTruck = (id) =>
  client.get(`/api/trucks/${id}`).then((r) => r.data)

export const createTruck = (data) =>
  client.post('/api/trucks/', data).then((r) => r.data)

export const updateTruck = (id, data) =>
  client.put(`/api/trucks/${id}`, data).then((r) => r.data)

export const deleteTruck = (id) =>
  client.delete(`/api/trucks/${id}`)
