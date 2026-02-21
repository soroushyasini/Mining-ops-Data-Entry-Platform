import { useForm } from 'react-hook-form'
import { useQuery } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import Input from '../ui/Input'
import Select from '../ui/Select'
import Button from '../ui/Button'
import JalaliDatePicker from '../ui/JalaliDatePicker'
import DriverAutoFill from '../ui/DriverAutoFill'
import { getFacilities } from '../../api/facilities'
import { getTrucks } from '../../api/trucks'
import { Lock } from 'lucide-react'

export default function ShipmentForm({ onSubmit, defaultValues = {}, loading = false }) {
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm({
    defaultValues,
  })

  const { data: facilities = [] } = useQuery({
    queryKey: ['facilities'],
    queryFn: () => getFacilities(),
  })
  const { data: trucks = [] } = useQuery({
    queryKey: ['trucks'],
    queryFn: () => getTrucks(),
  })

  const [dateValue, setDateValue] = useState(defaultValues.date || '')
  const [costPerTon, setCostPerTon] = useState(defaultValues.cost_per_ton_rial || '')
  const tonnageKg = watch('tonnage_kg')

  const totalCost = tonnageKg && costPerTon
    ? (parseFloat(tonnageKg) / 1000) * parseFloat(costPerTon)
    : null

  const facilityOptions = facilities.map((f) => ({ value: f.id, label: `${f.code} - ${f.name_fa}` }))
  const truckOptions = trucks.map((t) => ({ value: t.id, label: t.number }))

  const handleLookup = (lookupData) => {
    if (lookupData?.driver?.id) setValue('driver_id', lookupData.driver.id)
    if (lookupData?.facility?.id) setValue('facility_id', lookupData.facility.id)
    if (lookupData?.truck?.id) setValue('truck_id', lookupData.truck.id)
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
        <DriverAutoFill onLookup={handleLookup} />
        <JalaliDatePicker
          label="تاریخ"
          value={dateValue}
          onChange={setDateValue}
          error={errors.date?.message}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="شماره رسید"
          {...register('receipt_number')}
        />
        <Select
          label="ماشین"
          options={truckOptions}
          {...register('truck_id', { valueAsNumber: true })}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="تناژ (کیلوگرم)"
          type="number"
          step="0.01"
          error={errors.tonnage_kg?.message}
          {...register('tonnage_kg', { required: 'تناژ الزامی است', valueAsNumber: true })}
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
            <Lock size={13} className="text-slate-400" /> نرخ حمل (ریال/تن)
          </label>
          <input
            className="input-readonly w-full border border-slate-200 rounded-lg px-3 py-2 text-sm bg-slate-100 text-slate-600"
            readOnly
            value={costPerTon ? new Intl.NumberFormat('fa-IR').format(costPerTon) : '—'}
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700 flex items-center gap-1">
            <Lock size={13} className="text-slate-400" /> مجموع هزینه (ریال)
          </label>
          <input
            className="input-readonly w-full border border-slate-200 rounded-lg px-3 py-2 text-sm bg-slate-100 text-slate-600"
            readOnly
            value={totalCost ? new Intl.NumberFormat('fa-IR').format(Math.round(totalCost)) : '—'}
          />
        </div>
      </div>

      <Input label="مقصد" {...register('destination')} />
      <Input label="یادداشت" {...register('notes')} />

      <div className="flex justify-end gap-3 pt-2">
        <Button type="submit" disabled={loading}>
          {loading ? 'در حال ذخیره...' : 'ذخیره'}
        </Button>
      </div>
    </form>
  )
}
