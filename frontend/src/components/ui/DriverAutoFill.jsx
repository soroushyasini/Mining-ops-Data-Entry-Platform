import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { lookupTruck } from '../../api/lookup'
import { CheckCircle, AlertCircle, Lock } from 'lucide-react'
import Input from './Input'

function maskBankAccount(account) {
  if (!account) return null
  if (account.length <= 6) return account
  return account.slice(0, 2) + '...' + account.slice(-4)
}

function formatRial(amount) {
  if (!amount) return '—'
  return new Intl.NumberFormat('fa-IR').format(amount) + ' ریال'
}

export default function DriverAutoFill({ onLookup }) {
  const [truckNumber, setTruckNumber] = useState('')
  const [debouncedNumber, setDebouncedNumber] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedNumber(truckNumber.trim())
    }, 600)
    return () => clearTimeout(timer)
  }, [truckNumber])

  const { data, isLoading, isError } = useQuery({
    queryKey: ['lookup-truck', debouncedNumber],
    queryFn: () => lookupTruck(debouncedNumber),
    enabled: debouncedNumber.length >= 4,
    retry: false,
  })

  useEffect(() => {
    if (data && onLookup) {
      onLookup(data)
    }
  }, [data, onLookup])

  const found = data?.found
  const driver = data?.driver
  const facility = data?.facility
  const costPerTon = data?.cost_per_ton_rial

  return (
    <div className="space-y-3">
      <Input
        label="شماره ماشین"
        value={truckNumber}
        onChange={(e) => setTruckNumber(e.target.value)}
        placeholder="مثلاً: ۴۸۲۹۷"
      />

      {isLoading && debouncedNumber && (
        <div className="text-sm text-slate-500 animate-pulse">در حال جستجو...</div>
      )}

      {debouncedNumber.length >= 4 && !isLoading && data && (
        <>
          {found ? (
            <div className="border border-green-200 bg-green-50 rounded-xl p-4 space-y-2 animate-in fade-in">
              <div className="flex items-center gap-2 text-green-700">
                <CheckCircle size={18} />
                <span className="font-semibold text-sm">ماشین شناسایی شد</span>
              </div>
              {driver && (
                <div>
                  <p className="text-slate-500 text-xs">راننده</p>
                  <p className="font-bold text-slate-800 text-base">{driver.canonical_name}</p>
                  {driver.bank_account && (
                    <p className="text-sm text-slate-500 flex items-center gap-1">
                      <Lock size={12} />
                      شبا: {maskBankAccount(driver.bank_account)}
                    </p>
                  )}
                </div>
              )}
              {facility && (
                <div className="flex items-center gap-2">
                  <span className="badge-blue">{facility.code}</span>
                  <span className="text-sm text-slate-700">{facility.name_fa}</span>
                  {facility.truck_destination && (
                    <span className="text-xs text-slate-400">← {facility.truck_destination}</span>
                  )}
                </div>
              )}
              {costPerTon && (
                <div className="text-sm text-slate-600">
                  نرخ حمل: <span className="font-semibold text-slate-800">{formatRial(costPerTon)}</span>
                </div>
              )}
            </div>
          ) : (
            <div className="border border-red-200 bg-red-50 rounded-xl p-3 flex items-center gap-2 text-red-700 text-sm">
              <AlertCircle size={16} />
              شماره ماشین در سامانه ثبت نشده
            </div>
          )}
        </>
      )}
    </div>
  )
}
