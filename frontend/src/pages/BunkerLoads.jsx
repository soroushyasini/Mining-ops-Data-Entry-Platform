import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Upload } from 'lucide-react'
import Card from '../components/ui/Card'
import Table from '../components/ui/Table'
import Modal from '../components/ui/Modal'
import Button from '../components/ui/Button'
import FilterBar from '../components/ui/FilterBar'
import StatsCards from '../components/ui/StatsCards'
import BulkImportForm from '../components/forms/BulkImportForm'
import BunkerLoadForm from '../components/forms/BunkerLoadForm'
import { showToast, Toast } from '../components/ui/Toast'
import { getFacilities } from '../api/facilities'
import { getDrivers } from '../api/drivers'
import {
  getBunkerLoads,
  getBunkerLoadStats,
  createBunkerLoad,
  updateBunkerLoad,
  deleteBunkerLoad,
  bulkPreviewBunkerLoads,
  bulkConfirmBunkerLoads,
} from '../api/bunkerLoads'

const COLUMNS = [
  { key: 'date', label: 'تاریخ' },
  { key: 'time', label: 'ساعت' },
  { key: 'truck_number_raw', label: 'شماره ماشین' },
  { key: 'receipt_number', label: 'شماره قبض' },
  { key: 'tonnage_kg', label: 'تناژ (kg)' },
  { key: 'origin', label: 'مبدا' },
  { key: 'total_cost_rial', label: 'مبلغ (ریال)', render: (v) => v ? new Intl.NumberFormat('fa-IR').format(v) : '—' },
]

const EMPTY_FILTERS = { date_from: '', date_to: '', facility_id: null, driver_id: null }

export default function BunkerLoads() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editRecord, setEditRecord] = useState(null)
  const [deleteRecord, setDeleteRecord] = useState(null)
  const [showBulk, setShowBulk] = useState(false)
  const [previewData, setPreviewData] = useState(null)
  const [filters, setFilters] = useState(EMPTY_FILTERS)

  const filterParams = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v)
  )

  const { data: facilities = [] } = useQuery({
    queryKey: ['facilities'],
    queryFn: () => getFacilities(),
  })

  const { data: drivers = [] } = useQuery({
    queryKey: ['drivers'],
    queryFn: () => getDrivers(),
  })

  const { data = [], isLoading } = useQuery({
    queryKey: ['bunker-loads', filterParams],
    queryFn: () => getBunkerLoads({ ...filterParams, limit: 200 }),
  })

  const { data: stats } = useQuery({
    queryKey: ['bunker-loads-stats', filterParams],
    queryFn: () => getBunkerLoadStats(filterParams),
  })

  const createMutation = useMutation({
    mutationFn: createBunkerLoad,
    onSuccess: () => { qc.invalidateQueries(['bunker-loads']); setShowForm(false); showToast('ثبت شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => updateBunkerLoad(id, data),
    onSuccess: () => { qc.invalidateQueries(['bunker-loads']); setEditRecord(null); showToast('ویرایش شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteBunkerLoad,
    onSuccess: () => { qc.invalidateQueries(['bunker-loads']); setDeleteRecord(null); showToast('حذف شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const handlePreview = async (file) => {
    try {
      const data = await bulkPreviewBunkerLoads(file)
      setPreviewData(data)
    } catch (e) {
      showToast(e.message, 'error')
    }
  }

  const handleConfirm = async (data) => {
    try {
      const res = await bulkConfirmBunkerLoads(data)
      qc.invalidateQueries(['bunker-loads'])
      setShowBulk(false)
      setPreviewData(null)
      showToast(res.message)
    } catch (e) {
      showToast(e.message, 'error')
    }
  }

  return (
    <div className="space-y-6">
      <Toast />

      <FilterBar
        filters={filters}
        setFilters={setFilters}
        facilities={facilities}
        drivers={drivers}
        showDriverFilter
        onReset={() => setFilters(EMPTY_FILTERS)}
      />

      <StatsCards stats={stats} />

      <Card
        title="بارگیری بونکر"
        actions={
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => setShowBulk(true)}>
              <Upload size={14} /> آپلود اکسل
            </Button>
            <Button size="sm" onClick={() => setShowForm(true)}>
              <Plus size={14} /> افزودن
            </Button>
          </div>
        }
      >
        <Table
          columns={COLUMNS}
          data={data}
          loading={isLoading}
          onEdit={(row) => setEditRecord(row)}
          onDelete={(row) => setDeleteRecord(row)}
        />
      </Card>

      {/* Add Modal */}
      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="افزودن بارگیری">
        <BunkerLoadForm
          onSubmit={(d) => createMutation.mutate(d)}
          loading={createMutation.isPending}
        />
      </Modal>

      {/* Edit Modal */}
      <Modal isOpen={!!editRecord} onClose={() => setEditRecord(null)} title="ویرایش بارگیری">
        {editRecord && (
          <BunkerLoadForm
            defaultValues={editRecord}
            onSubmit={(d) => updateMutation.mutate({ id: editRecord.id, data: d })}
            loading={updateMutation.isPending}
          />
        )}
      </Modal>

      {/* Delete Confirm */}
      <Modal isOpen={!!deleteRecord} onClose={() => setDeleteRecord(null)} title="حذف" size="sm">
        <p className="text-slate-700 mb-4">آیا از حذف این رکورد اطمینان دارید؟</p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteRecord(null)}>انصراف</Button>
          <Button variant="danger" onClick={() => deleteMutation.mutate(deleteRecord.id)}>حذف</Button>
        </div>
      </Modal>

      {/* Bulk Import */}
      <BulkImportForm
        isOpen={showBulk}
        onClose={() => { setShowBulk(false); setPreviewData(null) }}
        onPreview={handlePreview}
        onConfirm={handleConfirm}
        previewData={previewData}
      />
    </div>
  )
}
