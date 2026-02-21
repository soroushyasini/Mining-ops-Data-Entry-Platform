import { useForm } from 'react-hook-form'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import Input from '../ui/Input'
import Select from '../ui/Select'
import Button from '../ui/Button'
import JalaliDatePicker from '../ui/JalaliDatePicker'
import { getDrivers } from '../../api/drivers'

export default function PaymentForm({ onSubmit, defaultValues = {}, loading = false }) {
  const { register, handleSubmit, formState: { errors } } = useForm({ defaultValues })
  const [dateValue, setDateValue] = useState(defaultValues.date || '')

  const { data: drivers = [] } = useQuery({
    queryKey: ['drivers'],
    queryFn: () => getDrivers(),
  })

  const driverOptions = drivers.map((d) => ({ value: d.id, label: d.canonical_name }))
  const paymentTypeOptions = [
    { value: 'owed', label: 'بدهی' },
    { value: 'paid', label: 'پرداخت شده' },
  ]

  const onFormSubmit = (data) => {
    onSubmit({ ...data, date: dateValue })
  }

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <Select
          label="راننده"
          options={driverOptions}
          error={errors.driver_id?.message}
          {...register('driver_id', { required: 'راننده الزامی است', valueAsNumber: true })}
        />
        <JalaliDatePicker label="تاریخ" value={dateValue} onChange={setDateValue} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="مبلغ (ریال)"
          type="number"
          error={errors.amount_rial?.message}
          {...register('amount_rial', { required: 'مبلغ الزامی است', valueAsNumber: true })}
        />
        <Select
          label="نوع پرداخت"
          options={paymentTypeOptions}
          error={errors.payment_type?.message}
          {...register('payment_type', { required: 'نوع پرداخت الزامی است' })}
        />
      </div>

      <Input label="یادداشت" {...register('notes')} />

      <div className="flex justify-end gap-3 pt-2">
        <Button type="submit" disabled={loading}>
          {loading ? 'در حال ذخیره...' : 'ذخیره'}
        </Button>
      </div>
    </form>
  )
}
