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
import Badge from '../components/ui/Badge'
import { showToast, Toast } from '../components/ui/Toast'
import { getFacilities, createFacility, updateFacility, deleteFacility } from '../api/facilities'

const COLUMNS = [
  { key: 'code', label: 'کد', render: (v) => <Badge variant="blue">{v}</Badge> },
  { key: 'name_fa', label: 'نام فارسی' },
  { key: 'name_en', label: 'نام انگلیسی' },
  { key: 'truck_destination', label: 'مقصد ماشین' },
]

function FacilityForm({ onSubmit, defaultValues = {}, loading = false }) {
  const { register, handleSubmit, formState: { errors } } = useForm({ defaultValues })
  const codeOptions = [
    { value: 'A', label: 'A' },
    { value: 'B', label: 'B' },
    { value: 'C', label: 'C' },
  ]

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <Select
          label="کد"
          options={codeOptions}
          error={errors.code?.message}
          {...register('code', { required: 'کد الزامی است' })}
        />
        <Input label="نام فارسی" error={errors.name_fa?.message} {...register('name_fa', { required: 'نام الزامی است' })} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Input label="نام انگلیسی" {...register('name_en')} />
        <Input label="مقصد ماشین" {...register('truck_destination')} />
      </div>
      <Input label="نام شیت بونکر" {...register('bunker_sheet_name')} />
      <div className="flex justify-end gap-3">
        <Button type="submit" disabled={loading}>{loading ? 'در حال ذخیره...' : 'ذخیره'}</Button>
      </div>
    </form>
  )
}

export default function Facilities() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editRecord, setEditRecord] = useState(null)
  const [deleteRecord, setDeleteRecord] = useState(null)

  const { data = [], isLoading } = useQuery({
    queryKey: ['facilities'],
    queryFn: () => getFacilities({ limit: 200 }),
  })

  const createMutation = useMutation({
    mutationFn: createFacility,
    onSuccess: () => { qc.invalidateQueries(['facilities']); setShowForm(false); showToast('ثبت شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => updateFacility(id, data),
    onSuccess: () => { qc.invalidateQueries(['facilities']); setEditRecord(null); showToast('ویرایش شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteFacility,
    onSuccess: () => { qc.invalidateQueries(['facilities']); setDeleteRecord(null); showToast('حذف شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  return (
    <div className="space-y-6">
      <Toast />
      <Card
        title="تاسیسات"
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

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="افزودن تاسیسات">
        <FacilityForm onSubmit={(d) => createMutation.mutate(d)} loading={createMutation.isPending} />
      </Modal>

      <Modal isOpen={!!editRecord} onClose={() => setEditRecord(null)} title="ویرایش تاسیسات">
        {editRecord && (
          <FacilityForm
            defaultValues={editRecord}
            onSubmit={(d) => updateMutation.mutate({ id: editRecord.id, data: d })}
            loading={updateMutation.isPending}
          />
        )}
      </Modal>

      <Modal isOpen={!!deleteRecord} onClose={() => setDeleteRecord(null)} title="حذف" size="sm">
        <p className="text-slate-700 mb-4">آیا از حذف این تاسیسات اطمینان دارید؟</p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteRecord(null)}>انصراف</Button>
          <Button variant="danger" onClick={() => deleteMutation.mutate(deleteRecord.id)}>حذف</Button>
        </div>
      </Modal>
    </div>
  )
}
