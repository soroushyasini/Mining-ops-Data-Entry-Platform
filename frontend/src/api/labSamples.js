import client from './client'

export const getLabSamples = (params = {}) =>
  client.get('/api/lab-samples/', { params }).then((r) => r.data)

export const getLabSample = (id) =>
  client.get(`/api/lab-samples/${id}`).then((r) => r.data)

export const createLabSample = (data) =>
  client.post('/api/lab-samples/', data).then((r) => r.data)

export const updateLabSample = (id, data) =>
  client.put(`/api/lab-samples/${id}`, data).then((r) => r.data)

export const deleteLabSample = (id) =>
  client.delete(`/api/lab-samples/${id}`)

export const bulkPreviewLabSamples = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return client
    .post('/api/lab-samples/bulk-preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((r) => r.data)
}

export const bulkConfirmLabSamples = (previewData) =>
  client.post('/api/lab-samples/bulk-confirm', previewData).then((r) => r.data)
