import { forwardRef } from 'react'

const Select = forwardRef(function Select(
  { label, error, options = [], placeholder = 'انتخاب کنید...', className = '', ...props },
  ref
) {
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-slate-700">
          {label}
        </label>
      )}
      <select
        ref={ref}
        className={`input-field bg-white ${error ? 'border-red-400 focus:ring-red-500' : ''} ${className}`}
        {...props}
      >
        <option value="">{placeholder}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  )
})

export default Select
