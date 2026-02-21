const fmt = (n) => n ? new Intl.NumberFormat('fa-IR').format(Math.round(n)) : '۰'

export default function StatsCards({ stats }) {
  if (!stats) return null
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6" dir="rtl">
      <div className="bg-blue-50 border border-blue-100 rounded-2xl p-4">
        <p className="text-sm text-blue-600 mb-1">تعداد رکوردها</p>
        <p className="text-2xl font-bold text-blue-800">{fmt(stats.count)}</p>
      </div>
      <div className="bg-green-50 border border-green-100 rounded-2xl p-4">
        <p className="text-sm text-green-600 mb-1">مجموع تناژ (کیلوگرم)</p>
        <p className="text-2xl font-bold text-green-800">{fmt(stats.total_tonnage_kg)}</p>
      </div>
      <div className="bg-amber-50 border border-amber-100 rounded-2xl p-4">
        <p className="text-sm text-amber-600 mb-1">مجموع مبلغ (ریال)</p>
        <p className="text-2xl font-bold text-amber-800">{fmt(stats.total_cost_rial)}</p>
      </div>
    </div>
  )
}
