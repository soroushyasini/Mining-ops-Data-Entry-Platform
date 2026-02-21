import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import Card from '../components/ui/Card'
import Table from '../components/ui/Table'
import Modal from '../components/ui/Modal'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import TruckForm from '../components/forms/TruckForm'
import { showToast, Toast } from '../components/ui/Toast'
import { getTrucks, createTruck, updateTruck, deleteTruck } from '../api/trucks'

const COLUMNS = [
  { key: 'number', label: 'شماره ماشین' },
  { key: 'status', label: 'وضعیت', render: (v) => <Badge variant={v === 'active' ? 'green' : 'gray'}>{v === 'active' ? 'فعال' : 'غیرفعال'}</Badge> },
]

export default function Trucks() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editRecord, setEditRecord] = useState(null)
  const [deleteRecord, setDeleteRecord] = useState(null)

  const { data = [], isLoading } = useQuery({
    queryKey: ['trucks'],
    queryFn: () => getTrucks({ limit: 200 }),
  })

  const createMutation = useMutation({
    mutationFn: createTruck,
    onSuccess: () => { qc.invalidateQueries(['trucks']); setShowForm(false); showToast('ثبت شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => updateTruck(id, data),
    onSuccess: () => { qc.invalidateQueries(['trucks']); setEditRecord(null); showToast('ویرایش شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteTruck,
    onSuccess: () => { qc.invalidateQueries(['trucks']); setDeleteRecord(null); showToast('حذف شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  return (
    <div className="space-y-6">
      <Toast />
      <Card
        title="ماشینها"
        actions={
          <Button size="sm" onClick={() => setShowForm(true)}>
            <Plus size={14} /> افزودن
          </Button>
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

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="افزودن ماشین">
        <TruckForm onSubmit={(d) => createMutation.mutate(d)} loading={createMutation.isPending} />
      </Modal>

      <Modal isOpen={!!editRecord} onClose={() => setEditRecord(null)} title="ویرایش ماشین">
        {editRecord && (
          <TruckForm
            defaultValues={editRecord}
            onSubmit={(d) => updateMutation.mutate({ id: editRecord.id, data: d })}
            loading={updateMutation.isPending}
          />
        )}
      </Modal>

      <Modal isOpen={!!deleteRecord} onClose={() => setDeleteRecord(null)} title="حذف" size="sm">
        <p className="text-slate-700 mb-4">آیا از حذف این ماشین اطمینان دارید؟</p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteRecord(null)}>انصراف</Button>
          <Button variant="danger" onClick={() => deleteMutation.mutate(deleteRecord.id)}>حذف</Button>
        </div>
      </Modal>
    </div>
  )
}
