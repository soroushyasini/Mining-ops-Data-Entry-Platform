import { forwardRef } from 'react'

const Input = forwardRef(function Input(
  { label, error, readonly = false, className = '', ...props },
  ref
) {
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-slate-700">
          {label}
        </label>
      )}
      <input
        ref={ref}
        readOnly={readonly}
        className={`input-field ${readonly ? 'input-readonly' : ''} ${
          error ? 'border-red-400 focus:ring-red-500' : ''
        } ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  )
})

export default Input
