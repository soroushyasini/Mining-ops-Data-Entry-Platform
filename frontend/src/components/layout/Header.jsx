import { useLocation } from 'react-router-dom'

const PAGE_TITLES = {
  '/bunker-loads': 'بارگیری بونکر',
  '/shipments': 'حمل و نقل',
  '/lab-samples': 'نمونه آزمایشگاه',
  '/payments': 'پرداختها',
  '/transport-costs': 'نرخهای حمل',
  '/drivers': 'رانندگان',
  '/trucks': 'ماشینها',
  '/facilities': 'تاسیسات',
  '/alerts': 'هشدارها',
}

export default function Header() {
  const location = useLocation()
  const title = PAGE_TITLES[location.pathname] || 'سامانه ورود اطلاعات معدن'

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shrink-0">
      <h1 className="text-lg font-semibold text-slate-800">{title}</h1>
      <div className="text-sm text-slate-500">سامانه معدن</div>
    </header>
  )
}
