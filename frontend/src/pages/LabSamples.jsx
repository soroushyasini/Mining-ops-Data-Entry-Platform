import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Upload } from 'lucide-react'
import Card from '../components/ui/Card'
import Table from '../components/ui/Table'
import Modal from '../components/ui/Modal'
import Button from '../components/ui/Button'
import BulkImportForm from '../components/forms/BulkImportForm'
import LabSampleForm from '../components/forms/LabSampleForm'
import { showToast, Toast } from '../components/ui/Toast'
import {
  getLabSamples,
  createLabSample,
  updateLabSample,
  deleteLabSample,
  bulkPreviewLabSamples,
  bulkConfirmLabSamples,
} from '../api/labSamples'

const COLUMNS = [
  { key: 'sample_code', label: 'کد نمونه' },
  { key: 'sheet_name', label: 'شیت' },
  { key: 'au_ppm', label: 'Au (ppm)' },
  { key: 'sample_type', label: 'نوع' },
  { key: 'date', label: 'تاریخ' },
  {
    key: 'au_detected',
    label: 'شناسایی',
    render: (v) => v ? '✅' : '❌',
  },
]

export default function LabSamples() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editRecord, setEditRecord] = useState(null)
  const [deleteRecord, setDeleteRecord] = useState(null)
  const [showBulk, setShowBulk] = useState(false)
  const [previewData, setPreviewData] = useState(null)

  const { data = [], isLoading } = useQuery({
    queryKey: ['lab-samples'],
    queryFn: () => getLabSamples({ limit: 200 }),
  })

  const createMutation = useMutation({
    mutationFn: createLabSample,
    onSuccess: () => { qc.invalidateQueries(['lab-samples']); setShowForm(false); showToast('ثبت شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => updateLabSample(id, data),
    onSuccess: () => { qc.invalidateQueries(['lab-samples']); setEditRecord(null); showToast('ویرایش شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteLabSample,
    onSuccess: () => { qc.invalidateQueries(['lab-samples']); setDeleteRecord(null); showToast('حذف شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const handlePreview = async (file) => {
    try {
      const data = await bulkPreviewLabSamples(file)
      setPreviewData(data)
    } catch (e) {
      showToast(e.message, 'error')
    }
  }

  const handleConfirm = async (data) => {
    try {
      const res = await bulkConfirmLabSamples(data)
      qc.invalidateQueries(['lab-samples'])
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
        title="نمونه‌های آزمایشگاه"
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

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="افزودن نمونه" size="lg">
        <LabSampleForm onSubmit={(d) => createMutation.mutate(d)} loading={createMutation.isPending} />
      </Modal>

      <Modal isOpen={!!editRecord} onClose={() => setEditRecord(null)} title="ویرایش نمونه" size="lg">
        {editRecord && (
          <LabSampleForm
            defaultValues={editRecord}
            onSubmit={(d) => updateMutation.mutate({ id: editRecord.id, data: d })}
            loading={updateMutation.isPending}
          />
        )}
      </Modal>

      <Modal isOpen={!!deleteRecord} onClose={() => setDeleteRecord(null)} title="حذف" size="sm">
        <p className="text-slate-700 mb-4">آیا از حذف این رکورد اطمینان دارید؟</p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteRecord(null)}>انصراف</Button>
          <Button variant="danger" onClick={() => deleteMutation.mutate(deleteRecord.id)}>حذف</Button>
        </div>
      </Modal>

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
