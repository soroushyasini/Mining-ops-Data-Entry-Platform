import { useForm } from 'react-hook-form'
import Input from '../ui/Input'
import Select from '../ui/Select'
import Button from '../ui/Button'

export default function TruckForm({ onSubmit, defaultValues = {}, loading = false }) {
  const { register, handleSubmit, formState: { errors } } = useForm({ defaultValues })

  const statusOptions = [
    { value: 'active', label: 'فعال' },
    { value: 'inactive', label: 'غیرفعال' },
  ]

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="شماره ماشین"
          error={errors.number?.message}
          {...register('number', { required: 'شماره ماشین الزامی است' })}
        />
        <Select
          label="وضعیت"
          options={statusOptions}
          {...register('status')}
        />
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <Button type="submit" disabled={loading}>
          {loading ? 'در حال ذخیره...' : 'ذخیره'}
        </Button>
      </div>
    </form>
  )
}
