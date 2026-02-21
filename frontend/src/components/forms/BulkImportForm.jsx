import { useState, useCallback } from 'react'
import { Upload, CheckCircle, XCircle, AlertCircle, FileSpreadsheet } from 'lucide-react'
import Button from '../ui/Button'
import Modal from '../ui/Modal'

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

  const handlePreview = () => {
    if (file) onPreview(file)
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
    <Modal isOpen={isOpen} onClose={onClose} title="آپلود اکسل" size="xl">
      <div className="space-y-4">
        {/* Drop Zone */}
        {!previewData && (
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
        )}

        {/* Preview Table */}
        {previewData && (
          <div className="space-y-3">
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
          </div>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose}>انصراف</Button>
          {!previewData ? (
            <Button onClick={handlePreview} disabled={!file || loading}>
              <Upload size={14} />
              پیش‌نمایش
            </Button>
          ) : (
            <Button onClick={() => onConfirm(previewData)} disabled={loading || validCount + warningCount === 0}>
              <CheckCircle size={14} />
              ثبت ردیف‌های معتبر ({validCount + warningCount})
            </Button>
          )}
        </div>
      </div>
    </Modal>
  )
}
