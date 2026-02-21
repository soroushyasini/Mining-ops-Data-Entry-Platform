import { useState } from 'react'
import jalaali from 'jalaali-js'

/**
 * Jalali date picker with calendar dropdown.
 * Stores value as Jalali string "YYYY/MM/DD".
 */
export default function JalaliDatePicker({ label, value, onChange, error, required, placeholder = '۱۴۰۴/۰۱/۰۱' }) {
  const [open, setOpen] = useState(false)

  const getToday = () => jalaali.toJalaali(new Date())

  const [viewYear, setViewYear] = useState(() => {
    if (value) return parseInt(value.split('/')[0])
    return getToday().jy
  })
  const [viewMonth, setViewMonth] = useState(() => {
    if (value) return parseInt(value.split('/')[1])
    return getToday().jm
  })

  const MONTHS_FA = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']

  const daysInMonth = jalaali.jalaaliMonthLength(viewYear, viewMonth)

    const firstDay = (() => {
    const g = jalaali.toGregorian(viewYear, viewMonth, 1)
    const d = new Date(g.gy, g.gm - 1, g.gd).getDay() // 0=Sun
    return (d + 1) % 7 // shift: Sun→1, Mon→2, ..., Sat→0
  })()

  const handleDayClick = (day) => {
    const mm = String(viewMonth).padStart(2, '0')
    const dd = String(day).padStart(2, '0')
    onChange(`${viewYear}/${mm}/${dd}`)
    setOpen(false)
  }

  const prevMonth = () => {
    if (viewMonth === 1) { setViewMonth(12); setViewYear(y => y - 1) }
    else setViewMonth(m => m - 1)
  }
  const nextMonth = () => {
    if (viewMonth === 12) { setViewMonth(1); setViewYear(y => y + 1) }
    else setViewMonth(m => m + 1)
  }

  const selectedDay = value ? parseInt(value.split('/')[2]) : null
  const selectedMonth = value ? parseInt(value.split('/')[1]) : null
  const selectedYear = value ? parseInt(value.split('/')[0]) : null

  return (
    <div className="space-y-1 relative" dir="rtl">
      {label && (
        <label className="block text-sm font-medium text-slate-700">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <input
        type="text"
        readOnly
        value={value || ''}
        placeholder={placeholder}
        onClick={() => setOpen(o => !o)}
        className={`input-field cursor-pointer ${error ? 'border-red-400 focus:ring-red-500' : ''}`}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
      {open && (
        <div className="absolute top-full right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-xl z-50 p-3 w-72">
          {/* Header */}
          <div className="flex items-center justify-between mb-3">
            <button type="button" onClick={nextMonth} className="p-1 hover:bg-slate-100 rounded text-slate-600">›</button>
            <span className="font-bold text-slate-800 text-sm">
              {MONTHS_FA[viewMonth - 1]} {viewYear}
            </span>
            <button type="button" onClick={prevMonth} className="p-1 hover:bg-slate-100 rounded text-slate-600">‹</button>
          </div>
          {/* Weekday headers */}
          <div className="grid grid-cols-7 mb-1">
            {['ش','ی','د','س','چ','پ','ج'].map(d => (
              <div key={d} className="text-center text-xs text-slate-400 py-1">{d}</div>
            ))}
          </div>
          {/* Days grid */}
          <div className="grid grid-cols-7 gap-0.5">
            {Array(firstDay).fill(null).map((_, i) => <div key={`e${i}`} />)}
            {Array(daysInMonth).fill(null).map((_, i) => {
              const day = i + 1
              const isSelected = day === selectedDay && viewMonth === selectedMonth && viewYear === selectedYear
              return (
                <button
                  key={day}
                  type="button"
                  onClick={() => handleDayClick(day)}
                  className={`text-center text-sm py-1.5 rounded-lg transition-colors
                    ${isSelected
                      ? 'bg-blue-600 text-white font-bold'
                      : 'hover:bg-blue-50 text-slate-700'
                    }`}
                >
                  {day}
                </button>
              )
            })}
          </div>
          {/* Today button */}
          <div className="mt-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={() => {
                const j = getToday()
                setViewYear(j.jy)
                setViewMonth(j.jm)
                const mm = String(j.jm).padStart(2, '0')
                const dd = String(j.jd).padStart(2, '0')
                onChange(`${j.jy}/${mm}/${dd}`)
                setOpen(false)
              }}
              className="w-full text-center text-xs text-blue-600 hover:text-blue-800 py-1"
            >
              امروز
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
