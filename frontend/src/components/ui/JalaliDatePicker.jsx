import { useState } from 'react'
import { Calendar } from 'lucide-react'

/**
 * Simple Jalali date picker using jalaali-js for conversion.
 * Stores value as Jalali string "YYYY/MM/DD".
 */
export default function JalaliDatePicker({ label, value, onChange, error, ...props }) {
  const [inputValue, setInputValue] = useState(value || '')

  const handleChange = (e) => {
    const val = e.target.value
    setInputValue(val)
    if (onChange) onChange(val)
  }

  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-slate-700">
          {label}
        </label>
      )}
      <div className="relative">
        <input
          type="text"
          value={inputValue}
          onChange={handleChange}
          placeholder="۱۴۰۳/۰۱/۱۵"
          className={`input-field pl-10 ${error ? 'border-red-400 focus:ring-red-500' : ''}`}
          {...props}
        />
        <Calendar
          size={16}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"
        />
      </div>
      {error && <p className="text-xs text-red-500">{error}</p>}
      <p className="text-xs text-slate-400">فرمت: ۱۴۰۳/۰۶/۱۵</p>
    </div>
  )
}
