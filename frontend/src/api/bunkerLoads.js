import client from './client'

export const getBunkerLoads = (params = {}) =>
  client.get('/api/bunker-loads/', { params }).then((r) => r.data)

export const getBunkerLoad = (id) =>
  client.get(`/api/bunker-loads/${id}`).then((r) => r.data)

export const getBunkerLoadStats = (params = {}) =>
  client.get('/api/bunker-loads/stats/summary', { params }).then((r) => r.data)

export const createBunkerLoad = (data) =>
  client.post('/api/bunker-loads/', data).then((r) => r.data)

export const updateBunkerLoad = (id, data) =>
  client.put(`/api/bunker-loads/${id}`, data).then((r) => r.data)

export const deleteBunkerLoad = (id) =>
  client.delete(`/api/bunker-loads/${id}`)

export const bulkPreviewBunkerLoads = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return client
    .post('/api/bunker-loads/bulk-preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((r) => r.data)
}

export const bulkConfirmBunkerLoads = (previewData) =>
  client.post('/api/bunker-loads/bulk-confirm', previewData).then((r) => r.data)
