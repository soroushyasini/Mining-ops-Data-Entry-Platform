import { useForm } from 'react-hook-form'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import Input from '../ui/Input'
import Select from '../ui/Select'
import Button from '../ui/Button'
import JalaliDatePicker from '../ui/JalaliDatePicker'
import DriverAutoFill from '../ui/DriverAutoFill'
import { getFacilities } from '../../api/facilities'
import { Lock } from 'lucide-react'

export default function BunkerLoadForm({ onSubmit, defaultValues = {}, loading = false }) {
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm({
    defaultValues,
  })

  const { data: facilities = [] } = useQuery({
    queryKey: ['facilities'],
    queryFn: () => getFacilities(),
  })

  const [dateValue, setDateValue] = useState(defaultValues.date || '')
  const [costPerTon, setCostPerTon] = useState(defaultValues.cost_per_ton_rial || '')
  const tonnageKg = watch('tonnage_kg')

  const totalCost = tonnageKg && costPerTon
    ? parseFloat(tonnageKg) * parseFloat(costPerTon)
    : null

  const facilityOptions = facilities.map((f) => ({
    value: f.id,
    label: `${f.code} - ${f.name_fa}`,
  }))

  const handleLookup = (lookupData) => {
    if (lookupData?.driver?.id) {
      setValue('driver_id', lookupData.driver.id)
    }
    if (lookupData?.facility?.id) {
      setValue('facility_id', lookupData.facility.id)
    }
    if (lookupData?.cost_per_ton_rial) {
      setCostPerTon(lookupData.cost_per_ton_rial)
      setValue('cost_per_ton_rial', lookupData.cost_per_ton_rial)
    }
  }

  const onFormSubmit = (data) => {
    onSubmit({
      ...data,
      date: dateValue,
      cost_per_ton_rial: costPerTon ? parseFloat(costPerTon) : null,
      total_cost_rial: totalCost,
    })
  }

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <JalaliDatePicker
          label="تاریخ"
          value={dateValue}
          onChange={setDateValue}
          error={errors.date?.message}
          required
        />
        <Input
          label="ساعت"
          placeholder="HH:MM"
          {...register('time')}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <DriverAutoFill onLookup={handleLookup} />
        </div>
        <Input
          label="شماره ماشین"
          {...register('truck_number_raw')}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="شماره قبض"
          {...register('receipt_number')}
        />
        <Input
          label="تناژ (کیلوگرم)"
          type="number"
          step="0.01"
          error={errors.tonnage_kg?.message}
          {...register('tonnage_kg', { required: 'تناژ الزامی است', valueAsNumber: true })}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="مبدا"
          {...register('origin')}
        />
        <Select
          label="تاسیسات"
          options={facilityOptions}
          {...register('facility_id', { valueAsNumber: true })}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700 flex items-center gap-1">
            <Lock size={13} className="text-slate-400" /> هزینه حمل هر تن (ریال)
          </label>
          <input
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm bg-slate-100 text-slate-600"
            readOnly
            value={costPerTon ? new Intl.NumberFormat('fa-IR').format(costPerTon) : '—'}
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700 flex items-center gap-1">
            <Lock size={13} className="text-slate-400" /> مبلغ (ریال)
          </label>
          <input
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm bg-slate-100 text-slate-600"
            readOnly
            value={totalCost ? new Intl.NumberFormat('fa-IR').format(Math.round(totalCost)) : '—'}
          />
        </div>
      </div>

      <Input
        label="توضیحات"
        {...register('notes')}
      />

      <div className="flex justify-end gap-3 pt-2">
        <Button type="submit" disabled={loading}>
          {loading ? 'در حال ذخیره...' : 'ذخیره'}
        </Button>
      </div>
    </form>
  )
}
