import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Upload } from 'lucide-react'
import Card from '../components/ui/Card'
import Table from '../components/ui/Table'
import Modal from '../components/ui/Modal'
import Button from '../components/ui/Button'
import BulkImportForm from '../components/forms/BulkImportForm'
import BunkerLoadForm from '../components/forms/BunkerLoadForm'
import { showToast, Toast } from '../components/ui/Toast'
import {
  getBunkerLoads,
  createBunkerLoad,
  updateBunkerLoad,
  deleteBunkerLoad,
  bulkPreviewBunkerLoads,
  bulkConfirmBunkerLoads,
} from '../api/bunkerLoads'

const COLUMNS = [
  { key: 'date', label: 'تاریخ' },
  { key: 'tonnage_kg', label: 'تناژ (kg)' },
  { key: 'cumulative_tonnage_kg', label: 'تناژ تجمعی (kg)' },
  { key: 'sheet_name', label: 'شیت' },
  { key: 'transport_cost_rial', label: 'هزینه حمل (ریال)', render: (v) => v ? new Intl.NumberFormat('fa-IR').format(v) : '—' },
]

export default function BunkerLoads() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editRecord, setEditRecord] = useState(null)
  const [deleteRecord, setDeleteRecord] = useState(null)
  const [showBulk, setShowBulk] = useState(false)
  const [previewData, setPreviewData] = useState(null)

  const { data = [], isLoading } = useQuery({
    queryKey: ['bunker-loads'],
    queryFn: () => getBunkerLoads({ limit: 200 }),
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
