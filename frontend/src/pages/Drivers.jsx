import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import Card from '../components/ui/Card'
import Table from '../components/ui/Table'
import Modal from '../components/ui/Modal'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import DriverForm from '../components/forms/DriverForm'
import { showToast, Toast } from '../components/ui/Toast'
import { getDrivers, createDriver, updateDriver, deleteDriver } from '../api/drivers'

function maskBank(acc) {
  if (!acc) return '—'
  return acc.length <= 6 ? acc : acc.slice(0, 2) + '...' + acc.slice(-4)
}

const COLUMNS = [
  { key: 'canonical_name', label: 'نام' },
  { key: 'phone', label: 'تلفن' },
  { key: 'bank_account', label: 'شبا', render: (v) => maskBank(v) },
  { key: 'status', label: 'وضعیت', render: (v) => <Badge variant={v === 'active' ? 'green' : 'gray'}>{v === 'active' ? 'فعال' : 'غیرفعال'}</Badge> },
]

export default function Drivers() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editRecord, setEditRecord] = useState(null)
  const [deleteRecord, setDeleteRecord] = useState(null)

  const { data = [], isLoading } = useQuery({
    queryKey: ['drivers'],
    queryFn: () => getDrivers({ limit: 200 }),
  })

  const parseAliases = (data) => {
    const aliasesStr = data.aliases_str || ''
    return {
      ...data,
      aliases: aliasesStr
        ? aliasesStr.split(',').map((s) => s.trim()).filter(Boolean)
        : [],
    }
  }

  const createMutation = useMutation({
    mutationFn: (d) => createDriver(parseAliases(d)),
    onSuccess: () => { qc.invalidateQueries(['drivers']); setShowForm(false); showToast('ثبت شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => updateDriver(id, parseAliases(data)),
    onSuccess: () => { qc.invalidateQueries(['drivers']); setEditRecord(null); showToast('ویرایش شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteDriver,
    onSuccess: () => { qc.invalidateQueries(['drivers']); setDeleteRecord(null); showToast('حذف شد') },
    onError: (e) => showToast(e.message, 'error'),
  })

  return (
    <div className="space-y-6">
      <Toast />
      <Card
        title="رانندگان"
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
          onEdit={(row) => setEditRecord({ ...row, aliases_str: (row.aliases || []).join(', ') })}
          onDelete={(row) => setDeleteRecord(row)}
        />
      </Card>

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="افزودن راننده">
        <DriverForm onSubmit={(d) => createMutation.mutate(d)} loading={createMutation.isPending} />
      </Modal>

      <Modal isOpen={!!editRecord} onClose={() => setEditRecord(null)} title="ویرایش راننده">
        {editRecord && (
          <DriverForm
            defaultValues={editRecord}
            onSubmit={(d) => updateMutation.mutate({ id: editRecord.id, data: d })}
            loading={updateMutation.isPending}
          />
        )}
      </Modal>

      <Modal isOpen={!!deleteRecord} onClose={() => setDeleteRecord(null)} title="حذف" size="sm">
        <p className="text-slate-700 mb-4">آیا از حذف این راننده اطمینان دارید؟</p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteRecord(null)}>انصراف</Button>
          <Button variant="danger" onClick={() => deleteMutation.mutate(deleteRecord.id)}>حذف</Button>
        </div>
      </Modal>
    </div>
  )
}
