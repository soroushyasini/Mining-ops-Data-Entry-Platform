import { useForm } from 'react-hook-form'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import Input from '../ui/Input'
import Select from '../ui/Select'
import Button from '../ui/Button'
import JalaliDatePicker from '../ui/JalaliDatePicker'
import DriverAutoFill from '../ui/DriverAutoFill'
import { getFacilities } from '../../api/facilities'

export default function BunkerLoadForm({ onSubmit, defaultValues = {}, loading = false }) {
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm({
    defaultValues,
  })

  const { data: facilities = [] } = useQuery({
    queryKey: ['facilities'],
    queryFn: () => getFacilities(),
  })

  const [dateValue, setDateValue] = useState(defaultValues.date || '')

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
  }

  const onFormSubmit = (data) => {
    onSubmit({ ...data, date: dateValue })
  }

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <DriverAutoFill onLookup={handleLookup} />
        </div>
        <div>
          <JalaliDatePicker
            label="تاریخ"
            value={dateValue}
            onChange={setDateValue}
            error={errors.date?.message}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="تناژ (کیلوگرم)"
          type="number"
          step="0.01"
          error={errors.tonnage_kg?.message}
          {...register('tonnage_kg', { required: 'تناژ الزامی است', valueAsNumber: true })}
        />
        <Input
          label="تناژ تجمعی (کیلوگرم)"
          type="number"
          step="0.01"
          {...register('cumulative_tonnage_kg', { valueAsNumber: true })}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Select
          label="تاسیسات"
          options={facilityOptions}
          {...register('facility_id', { valueAsNumber: true })}
        />
        <Input
          label="نام شیت"
          {...register('sheet_name')}
        />
      </div>

      <Input
        label="هزینه حمل (ریال)"
        type="number"
        {...register('transport_cost_rial', { valueAsNumber: true })}
      />

      <div className="flex justify-end gap-3 pt-2">
        <Button type="submit" disabled={loading}>
          {loading ? 'در حال ذخیره...' : 'ذخیره'}
        </Button>
      </div>
    </form>
  )
}
