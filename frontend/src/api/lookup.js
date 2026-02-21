import client from './client'

export const lookupTruck = (truckNumber) =>
  client.get(`/api/lookup/truck/${truckNumber}`).then((r) => r.data)
