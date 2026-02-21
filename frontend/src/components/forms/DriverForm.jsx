import { useForm } from 'react-hook-form'
import Input from '../ui/Input'
import Button from '../ui/Button'

export default function DriverForm({ onSubmit, defaultValues = {}, loading = false }) {
  const { register, handleSubmit, formState: { errors } } = useForm({ defaultValues })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      <Input
        label="نام کامل"
        error={errors.canonical_name?.message}
        {...register('canonical_name', { required: 'نام الزامی است' })}
      />
      <div className="grid grid-cols-2 gap-4">
        <Input label="شماره تماس" {...register('phone')} />
        <Input label="شماره شبا (IR...)" {...register('bank_account')} />
      </div>
      <Input label="نام‌های مستعار (با کاما جدا کنید)" {...register('aliases_str')} />

      <div className="flex justify-end gap-3 pt-2">
        <Button type="submit" disabled={loading}>
          {loading ? 'در حال ذخیره...' : 'ذخیره'}
        </Button>
      </div>
    </form>
  )
}
