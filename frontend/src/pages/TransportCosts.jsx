import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { useForm } from 'react-hook-form'
import Card from '../components/ui/Card'
import Table from '../components/ui/Table'
import Modal from '../components/ui/Modal'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Select from '../components/ui/Select'
import JalaliDatePicker from '../components/ui/JalaliDatePicker'
import { showToast, Toast } from '../components/ui/Toast'
import { getTransportCosts, createTransportCost, updateTransportCost, deleteTransportCost } from '../api/transportCosts'
import { getFacilities } from '../api/facilities'

const COLUMNS = [
  { key: 'route', label: 'مسیر' },
  { key: 'cost_per_ton_rial', label: 'نرخ (ریال/تن)', render: (v) => new Intl.NumberFormat('fa-IR').format(v) },
  { key: 'valid_from', label: 'از تاریخ' },
  { key: 'valid_to', label: 'تا تاریخ' },
]

function TransportCostForm({ onSubmit, defaultValues = {}, loading = false }) {
  const { register, handleSubmit, formState: { errors } } = useForm({ defaultValues })
  const [validFrom, setValidFrom] = useState(defaultValues.valid_from || '')
  const [validTo, setValidTo] = useState(defaultValues.valid_to || '')

  const { data: facilities = [] } = useQuery({
    queryKey: ['facilities'],
    queryFn: () => getFacilities(),
  })

  const facilityOptions = facilities.map((f) => ({ value: f.id, label: `${f.code} - ${f.name_fa}` }))

  return (
    <form onSubmit={handleSubmit((d) => onSubmit({ ...d, valid_from: validFrom, valid_to: validTo }))} className="space-y-5">
      <Input
        label="مسیر"
        error={errors.route?.message}
        {...register('route', { required: 'مسیر الزامی است' })}
      />
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="نرخ (ریال/تن)"
          type="number"
          error={errors.cost_per_ton_rial?.message}
          {...register('cost_per_ton_rial', { required: 'نرخ الزامی است', valueAsNumber: true })}
        />
        <Select
          label="تاسیسات"
          options={facilityOptions}
          {...register('facility_id', { valueAsNumber: true })}
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <JalaliDatePicker label="از تاریخ" value={validFrom} onChange={setValidFrom} />
        <JalaliDatePicker label="تا تاریخ" value={validTo} onChange={setValidTo} />
      </div>
      <div className="flex justify-end gap-3">
        <Button type="submit" disabled={loading}>{loading ? 'در حال ذخیره...' : 'ذخیره'}</Button>
      </div>
    </form>
  )
}

export default function TransportCosts() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editRecord, setEditRecord] = useState(null)
  const [deleteRecord, setDeleteRecord] = useState(null)

  const { data = [], isLoading } = useQuery({
    queryKey: ['transport-costs'],
    queryFn: () => getTransportCosts({ limit: 200 }),
  })

  const createMutation = useMutation({
    mutationFn: createTransportCost,
    onSuccess: () => { qc.invalidateQueries(['transport-costs']); setShowForm(false); showToast('ثبت شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => updateTransportCost(id, data),
    onSuccess: () => { qc.invalidateQueries(['transport-costs']); setEditRecord(null); showToast('ویرایش شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteTransportCost,
    onSuccess: () => { qc.invalidateQueries(['transport-costs']); setDeleteRecord(null); showToast('حذف شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  return (
    <div className="space-y-6">
      <Toast />
      <Card
        title="نرخهای حمل"
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

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="افزودن نرخ حمل">
        <TransportCostForm onSubmit={(d) => createMutation.mutate(d)} loading={createMutation.isPending} />
      </Modal>

      <Modal isOpen={!!editRecord} onClose={() => setEditRecord(null)} title="ویرایش نرخ حمل">
        {editRecord && (
          <TransportCostForm
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
