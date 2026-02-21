import { useForm } from 'react-hook-form'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import Input from '../ui/Input'
import Select from '../ui/Select'
import Button from '../ui/Button'
import JalaliDatePicker from '../ui/JalaliDatePicker'
import { getFacilities } from '../../api/facilities'

export default function LabSampleForm({ onSubmit, defaultValues = {}, loading = false }) {
  const { register, handleSubmit, formState: { errors } } = useForm({ defaultValues })
  const [dateValue, setDateValue] = useState(defaultValues.date || '')

  const { data: facilities = [] } = useQuery({
    queryKey: ['facilities'],
    queryFn: () => getFacilities(),
  })

  const facilityOptions = facilities.map((f) => ({ value: f.id, label: `${f.code} - ${f.name_fa}` }))

  const onFormSubmit = (data) => {
    onSubmit({ ...data, date: dateValue })
  }

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="کد نمونه"
          error={errors.sample_code?.message}
          {...register('sample_code', { required: 'کد نمونه الزامی است' })}
        />
        <Input
          label="نام شیت"
          error={errors.sheet_name?.message}
          {...register('sheet_name', { required: 'نام شیت الزامی است' })}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Au (ppm)"
          type="number"
          step="0.0001"
          {...register('au_ppm', { valueAsNumber: true })}
        />
        <Select
          label="تاسیسات"
          options={facilityOptions}
          {...register('facility_id', { valueAsNumber: true })}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <JalaliDatePicker label="تاریخ" value={dateValue} onChange={setDateValue} />
        <Input
          label="نوع نمونه"
          {...register('sample_type')}
        />
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Input label="سال" type="number" {...register('year', { valueAsNumber: true })} />
        <Input label="ماه" type="number" {...register('month', { valueAsNumber: true })} />
        <Input label="روز" type="number" {...register('day', { valueAsNumber: true })} />
      </div>

      <div className="flex items-center gap-6">
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input type="checkbox" {...register('au_detected')} className="rounded" />
          Au شناسایی شد
        </label>
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input type="checkbox" {...register('below_detection_limit')} className="rounded" />
          زیر حد تشخیص
        </label>
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input type="checkbox" {...register('is_special')} className="rounded" />
          نمونه ویژه
        </label>
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <Button type="submit" disabled={loading}>
          {loading ? 'در حال ذخیره...' : 'ذخیره'}
        </Button>
      </div>
    </form>
  )
}
