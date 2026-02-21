import client from './client'

export const getShipments = (params = {}) =>
  client.get('/api/shipments/', { params }).then((r) => r.data)

export const getShipment = (id) =>
  client.get(`/api/shipments/${id}`).then((r) => r.data)

export const createShipment = (data) =>
  client.post('/api/shipments/', data).then((r) => r.data)

export const updateShipment = (id, data) =>
  client.put(`/api/shipments/${id}`, data).then((r) => r.data)

export const deleteShipment = (id) =>
  client.delete(`/api/shipments/${id}`)

export const bulkPreviewShipments = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return client
    .post('/api/shipments/bulk-preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((r) => r.data)
}

export const bulkConfirmShipments = (previewData) =>
  client.post('/api/shipments/bulk-confirm', previewData).then((r) => r.data)
