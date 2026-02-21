import JalaliDatePicker from './JalaliDatePicker'

/**
 * Reusable filter bar for list pages.
 * Props:
 *   filters: { date_from, date_to, facility_id, driver_id }
 *   setFilters: setter
 *   facilities: array of facility objects
 *   drivers: array of driver objects (optional)
 *   showDriverFilter: bool
 *   onReset: fn
 */
export default function FilterBar({ filters, setFilters, facilities = [], drivers = [], showDriverFilter = false, onReset }) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 mb-6 shadow-sm" dir="rtl">
      <div className="flex flex-wrap gap-4 items-end">
        {/* Date From */}
        <div className="min-w-[160px]">
          <JalaliDatePicker
            label="از تاریخ"
            value={filters.date_from || ''}
            onChange={v => setFilters(f => ({ ...f, date_from: v }))}
          />
        </div>
        {/* Date To */}
        <div className="min-w-[160px]">
          <JalaliDatePicker
            label="تا تاریخ"
            value={filters.date_to || ''}
            onChange={v => setFilters(f => ({ ...f, date_to: v }))}
          />
        </div>
        {/* Facility */}
        {facilities.length > 0 && (
          <div className="min-w-[160px]">
            <label className="block text-sm font-medium text-slate-700 mb-1">تاسیسات</label>
            <select
              value={filters.facility_id || ''}
              onChange={e => setFilters(f => ({ ...f, facility_id: e.target.value || null }))}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-right bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">همه</option>
              {facilities.map(f => (
                <option key={f.id} value={f.id}>{f.name_fa} ({f.code})</option>
              ))}
            </select>
          </div>
        )}
        {/* Driver */}
        {showDriverFilter && drivers.length > 0 && (
          <div className="min-w-[200px]">
            <label className="block text-sm font-medium text-slate-700 mb-1">راننده</label>
            <select
              value={filters.driver_id || ''}
              onChange={e => setFilters(f => ({ ...f, driver_id: e.target.value || null }))}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-right bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">همه</option>
              {drivers.map(d => (
                <option key={d.id} value={d.id}>{d.canonical_name}</option>
              ))}
            </select>
          </div>
        )}
        {/* Reset button */}
        <button
          onClick={onReset}
          className="px-4 py-2 text-sm text-slate-600 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
        >
          پاک کردن فیلتر
        </button>
      </div>
    </div>
  )
}
