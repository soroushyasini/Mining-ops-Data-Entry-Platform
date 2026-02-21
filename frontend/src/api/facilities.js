import client from './client'

export const getFacilities = (params = {}) =>
  client.get('/api/facilities/', { params }).then((r) => r.data)

export const getFacility = (id) =>
  client.get(`/api/facilities/${id}`).then((r) => r.data)

export const createFacility = (data) =>
  client.post('/api/facilities/', data).then((r) => r.data)

export const updateFacility = (id, data) =>
  client.put(`/api/facilities/${id}`, data).then((r) => r.data)

export const deleteFacility = (id) =>
  client.delete(`/api/facilities/${id}`)
