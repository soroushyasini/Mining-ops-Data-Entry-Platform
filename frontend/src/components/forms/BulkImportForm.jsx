import { useState, useCallback } from 'react'
import { Upload, CheckCircle, XCircle, AlertCircle, FileSpreadsheet, ArrowRight } from 'lucide-react'
import Button from '../ui/Button'
import Modal from '../ui/Modal'
import client from '../../api/client'

const BUNKER_LOAD_FIELDS = [
  { key: 'date', label: 'تاریخ', required: true },
  { key: 'time', label: 'ساعت', required: false },
  { key: 'truck_number_raw', label: 'شماره ماشین', required: false },
  { key: 'receipt_number', label: 'شماره قبض', required: false },
  { key: 'tonnage_kg', label: 'تناژ', required: true },
  { key: 'origin', label: 'مبدا', required: false },
  { key: 'cost_per_ton_rial', label: 'هزینه حمل هر تن', required: false },
  { key: 'total_cost_rial', label: 'مبلغ (ریال)', required: false },
  { key: 'notes', label: 'توضیحات', required: false },
]

const AUTO_DETECT = {
  date: ['تاریخ', 'date'],
  time: ['ساعت', 'time'],
  truck_number_raw: ['شماره ماشین', 'پلاک', 'ماشین'],
  receipt_number: ['شماره قبض', 'قبض'],
  tonnage_kg: ['تناژ', 'tonnage', 'وزن'],
  origin: ['مبدا', 'origin'],
  cost_per_ton_rial: ['هزینه حمل هر تن', 'نرخ', 'هزینه'],
  total_cost_rial: ['مبلغ', 'ریال', 'total'],
  notes: ['توضیحات', 'notes', 'یادداشت'],
}

function autoDetectMapping(headers) {
  const mapping = {}
  for (const [field, hints] of Object.entries(AUTO_DETECT)) {
    for (const header of headers) {
      if (hints.some(h => header.includes(h))) {
        mapping[field] = header
        break
      }
    }
  }
  return mapping
}

export default function BulkImportForm({
  isOpen,
  onClose,
  onPreview,
  onConfirm,
  previewData = null,
  loading = false,
}) {
  const [file, setFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [step, setStep] = useState('upload') // 'upload' | 'mapping' | 'preview'
  const [excelHeaders, setExcelHeaders] = useState([])
  const [mapping, setMapping] = useState({})
  const [fetchingHeaders, setFetchingHeaders] = useState(false)

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped && dropped.name.endsWith('.xlsx')) {
      setFile(dropped)
    }
  }, [])

  const handleFileChange = (e) => {
    const selected = e.target.files[0]
    if (selected) setFile(selected)
  }

  const handleUploadNext = async () => {
    if (!file) return
    setFetchingHeaders(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await client.post('/api/bunker-loads/excel-headers', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      const headers = res.data.headers || []
      setExcelHeaders(headers)
      setMapping(autoDetectMapping(headers))
      setStep('mapping')
    } catch {
      // fallback: go directly to preview
      onPreview(file)
      setStep('preview')
    } finally {
      setFetchingHeaders(false)
    }
  }

  const handleMappingConfirm = () => {
    setStep('preview')
    onPreview(file)
  }

  const handleClose = () => {
    setFile(null)
    setStep('upload')
    setExcelHeaders([])
    setMapping({})
    onClose()
  }

  const statusIcon = (status) => {
    if (status === 'valid') return <CheckCircle size={14} className="text-green-500" />
    if (status === 'warning') return <AlertCircle size={14} className="text-amber-500" />
    return <XCircle size={14} className="text-red-500" />
  }

  const validCount = previewData?.valid_count || 0
  const warningCount = previewData?.warning_count || 0
  const errorCount = previewData?.error_count || 0

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="آپلود اکسل" size="xl">
      <div className="space-y-4">
        {/* Step 1: Upload */}
        {step === 'upload' && (
          <>
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                isDragging ? 'border-blue-400 bg-blue-50' : 'border-slate-300 hover:border-slate-400'
              }`}
            >
              <FileSpreadsheet size={40} className="mx-auto text-slate-400 mb-3" />
              <p className="text-slate-600 mb-2">فایل اکسل را اینجا بکشید یا</p>
              <label className="cursor-pointer">
                <span className="text-blue-500 hover:text-blue-600 font-medium">انتخاب فایل</span>
                <input
                  type="file"
                  accept=".xlsx"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </label>
              {file && (
                <p className="mt-2 text-sm text-green-600 flex items-center justify-center gap-1">
                  <CheckCircle size={14} />
                  {file.name}
                </p>
              )}
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <Button variant="secondary" onClick={handleClose}>انصراف</Button>
              <Button onClick={handleUploadNext} disabled={!file || loading || fetchingHeaders}>
                <ArrowRight size={14} />
                {fetchingHeaders ? 'در حال خواندن...' : 'بعدی: تطبیق ستون‌ها'}
              </Button>
            </div>
          </>
        )}

        {/* Step 2: Column Mapping */}
        {step === 'mapping' && (
          <>
            <p className="text-sm text-slate-600 mb-3" dir="rtl">
              ستون‌های اکسل را به فیلدهای سیستم نگاشت کنید:
            </p>
            <div className="overflow-x-auto rounded-xl border border-slate-200" dir="rtl">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-4 py-2 text-right text-slate-600">فیلد سیستم</th>
                    <th className="px-4 py-2 text-right text-slate-600">ستون اکسل</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {BUNKER_LOAD_FIELDS.map(({ key, label, required }) => (
                    <tr key={key}>
                      <td className="px-4 py-2 text-slate-700">
                        {label} {required && <span className="text-red-500 text-xs">(اجباری)</span>}
                      </td>
                      <td className="px-4 py-2">
                        <select
                          value={mapping[key] || ''}
                          onChange={e => setMapping(m => ({ ...m, [key]: e.target.value || undefined }))}
                          className="w-full px-2 py-1 border border-slate-300 rounded-lg text-right bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                        >
                          <option value="">— انتخاب نشده —</option>
                          {excelHeaders.map(h => (
                            <option key={h} value={h}>{h}</option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <Button variant="secondary" onClick={() => setStep('upload')}>بازگشت</Button>
              <Button onClick={handleMappingConfirm} disabled={loading}>
                <Upload size={14} />
                پیش‌نمایش و تأیید
              </Button>
            </div>
          </>
        )}

        {/* Step 3: Preview & Confirm */}
        {step === 'preview' && previewData && (
          <>
            <div className="flex items-center gap-4 text-sm">
              <span className="text-green-600 flex items-center gap-1">
                <CheckCircle size={14} /> {validCount} ردیف آماده
              </span>
              <span className="text-amber-600 flex items-center gap-1">
                <AlertCircle size={14} /> {warningCount} هشدار
              </span>
              <span className="text-red-600 flex items-center gap-1">
                <XCircle size={14} /> {errorCount} خطا
              </span>
            </div>

            <div className="max-h-64 overflow-y-auto rounded-xl border border-slate-200">
              <table className="w-full text-xs">
                <thead className="bg-slate-50 sticky top-0">
                  <tr>
                    <th className="px-3 py-2 text-right text-slate-600">ردیف</th>
                    <th className="px-3 py-2 text-right text-slate-600">وضعیت</th>
                    <th className="px-3 py-2 text-right text-slate-600">پیام</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {previewData.rows?.map((row) => (
                    <tr key={row.row_num}>
                      <td className="px-3 py-2 text-slate-700">{row.row_num}</td>
                      <td className="px-3 py-2">
                        <div className="flex items-center gap-1">
                          {statusIcon(row.status)}
                          <span className={
                            row.status === 'valid' ? 'text-green-700' :
                            row.status === 'warning' ? 'text-amber-700' : 'text-red-700'
                          }>
                            {row.status === 'valid' ? 'معتبر' : row.status === 'warning' ? 'هشدار' : 'خطا'}
                          </span>
                        </div>
                      </td>
                      <td className="px-3 py-2 text-slate-600">{row.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <Button variant="secondary" onClick={handleClose}>انصراف</Button>
              <Button onClick={() => onConfirm(previewData)} disabled={loading || validCount + warningCount === 0}>
                <CheckCircle size={14} />
                ثبت ردیف‌های معتبر ({validCount + warningCount})
              </Button>
            </div>
          </>
        )}

        {/* Waiting for preview */}
        {step === 'preview' && !previewData && (
          <div className="text-center py-8 text-slate-500">در حال بارگذاری پیش‌نمایش...</div>
        )}
      </div>
    </Modal>
  )
}
