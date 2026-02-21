import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import { Bell, Info, AlertTriangle, AlertCircle } from 'lucide-react'

const SAMPLE_ALERTS = [
  { id: 1, level: 'info', rule: 'low_tonnage', message: 'تناژ بارگیری روز جاری کمتر از میانگین ماهانه است', created_at: '۱۴۰۳/۰۶/۱۵', acknowledged: false },
  { id: 2, level: 'warning', rule: 'missing_lab_sample', message: 'نمونه آزمایشگاه برای شیت A در هفته جاری ثبت نشده', created_at: '۱۴۰۳/۰۶/۱۴', acknowledged: false },
  { id: 3, level: 'critical', rule: 'cost_spike', message: 'افزایش ۳۰٪ در هزینه حمل نسبت به ماه قبل', created_at: '۱۴۰۳/۰۶/۱۳', acknowledged: true },
]

const levelIcon = {
  info: <Info size={18} className="text-blue-500" />,
  warning: <AlertTriangle size={18} className="text-amber-500" />,
  critical: <AlertCircle size={18} className="text-red-500" />,
}

const levelBadge = {
  info: <Badge variant="blue">اطلاعات</Badge>,
  warning: <Badge variant="amber">هشدار</Badge>,
  critical: <Badge variant="red">بحرانی</Badge>,
}

export default function Alerts() {
  return (
    <div className="space-y-6">
      <Card title="هشدارها">
        <div className="space-y-3">
          {SAMPLE_ALERTS.map((alert) => (
            <div
              key={alert.id}
              className={`flex items-start gap-4 p-4 rounded-xl border ${
                alert.acknowledged
                  ? 'bg-slate-50 border-slate-200 opacity-60'
                  : 'bg-white border-slate-200 shadow-sm'
              }`}
            >
              <div className="mt-0.5">{levelIcon[alert.level]}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  {levelBadge[alert.level]}
                  <span className="text-xs text-slate-400">{alert.created_at}</span>
                  {alert.acknowledged && (
                    <Badge variant="gray">تایید شده</Badge>
                  )}
                </div>
                <p className="text-sm text-slate-700">{alert.message}</p>
                <p className="text-xs text-slate-400 mt-1">{alert.rule}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
