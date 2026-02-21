import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import Card from '../components/ui/Card'
import Table from '../components/ui/Table'
import Modal from '../components/ui/Modal'
import Button from '../components/ui/Button'
import PaymentForm from '../components/forms/PaymentForm'
import Badge from '../components/ui/Badge'
import { showToast, Toast } from '../components/ui/Toast'
import { getPayments, createPayment, updatePayment, deletePayment } from '../api/payments'

const COLUMNS = [
  { key: 'date', label: 'تاریخ' },
  { key: 'amount_rial', label: 'مبلغ (ریال)', render: (v) => new Intl.NumberFormat('fa-IR').format(v) },
  {
    key: 'payment_type',
    label: 'نوع',
    render: (v) => (
      <Badge variant={v === 'paid' ? 'green' : 'amber'}>
        {v === 'paid' ? 'پرداخت شده' : 'بدهی'}
      </Badge>
    ),
  },
  { key: 'notes', label: 'یادداشت' },
]

export default function Payments() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editRecord, setEditRecord] = useState(null)
  const [deleteRecord, setDeleteRecord] = useState(null)

  const { data = [], isLoading } = useQuery({
    queryKey: ['payments'],
    queryFn: () => getPayments({ limit: 200 }),
  })

  const createMutation = useMutation({
    mutationFn: createPayment,
    onSuccess: () => { qc.invalidateQueries(['payments']); setShowForm(false); showToast('ثبت شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => updatePayment(id, data),
    onSuccess: () => { qc.invalidateQueries(['payments']); setEditRecord(null); showToast('ویرایش شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const deleteMutation = useMutation({
    mutationFn: deletePayment,
    onSuccess: () => { qc.invalidateQueries(['payments']); setDeleteRecord(null); showToast('حذف شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  return (
    <div className="space-y-6">
      <Toast />
      <Card
        title="پرداختها"
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

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="افزودن پرداخت">
        <PaymentForm onSubmit={(d) => createMutation.mutate(d)} loading={createMutation.isPending} />
      </Modal>

      <Modal isOpen={!!editRecord} onClose={() => setEditRecord(null)} title="ویرایش پرداخت">
        {editRecord && (
          <PaymentForm
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
    </div>
  )
}
