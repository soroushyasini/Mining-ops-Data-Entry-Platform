import { NavLink } from 'react-router-dom'
import {
  Package,
  Truck,
  FlaskConical,
  CreditCard,
  TrendingUp,
  User,
  Car,
  Building2,
  Bell,
} from 'lucide-react'

const NAV_ITEMS = [
  { path: '/bunker-loads', label: 'بارگیری بونکر', icon: Package },
  { path: '/shipments', label: 'حمل و نقل', icon: Truck },
  { path: '/lab-samples', label: 'نمونه آزمایشگاه', icon: FlaskConical },
  { path: '/payments', label: 'پرداختها', icon: CreditCard },
  { path: '/transport-costs', label: 'نرخهای حمل', icon: TrendingUp },
]

const REGISTRY_ITEMS = [
  { path: '/drivers', label: 'رانندگان', icon: User },
  { path: '/trucks', label: 'ماشینها', icon: Car },
  { path: '/facilities', label: 'تاسیسات', icon: Building2 },
  { path: '/alerts', label: 'هشدارها', icon: Bell },
]

export default function Sidebar() {
  return (
    <div className="w-60 bg-slate-900 flex flex-col h-full shrink-0">
      {/* Logo */}
      <div className="p-5 border-b border-slate-700">
        <div className="text-white font-bold text-base leading-tight">
          ⛏️ سامانه ورود اطلاعات معدن
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}

        {/* Divider */}
        <div className="pt-3 pb-1">
          <p className="text-xs text-slate-500 px-3 font-medium tracking-wider">
            رجیستری
          </p>
        </div>

        {REGISTRY_ITEMS.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
