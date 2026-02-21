import { useState } from 'react'
import { ChevronRight, ChevronLeft, Edit2, Trash2 } from 'lucide-react'
import Button from './Button'

export default function Table({
  columns = [],
  data = [],
  loading = false,
  pageSize = 10,
  onEdit,
  onDelete,
}) {
  const [page, setPage] = useState(1)

  const totalPages = Math.ceil(data.length / pageSize)
  const paginatedData = data.slice((page - 1) * pageSize, page * pageSize)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-40 text-slate-500">
        در حال بارگذاری...
      </div>
    )
  }

  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-40 text-slate-500">
        داده‌ای برای نمایش وجود ندارد
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto rounded-xl border border-slate-200">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-4 py-3 text-right font-semibold text-slate-600 whitespace-nowrap"
                >
                  {col.label}
                </th>
              ))}
              {(onEdit || onDelete) && (
                <th className="px-4 py-3 text-right font-semibold text-slate-600 w-24">
                  عملیات
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {paginatedData.map((row, idx) => (
              <tr
                key={row.id || idx}
                className="hover:bg-slate-50 transition-colors"
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3 text-slate-700">
                    {col.render ? col.render(row[col.key], row) : (row[col.key] ?? '—')}
                  </td>
                ))}
                {(onEdit || onDelete) && (
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      {onEdit && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => onEdit(row)}
                          title="ویرایش"
                        >
                          <Edit2 size={14} className="text-blue-500" />
                        </Button>
                      )}
                      {onDelete && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => onDelete(row)}
                          title="حذف"
                        >
                          <Trash2 size={14} className="text-red-500" />
                        </Button>
                      )}
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-sm text-slate-600">
          <span>
            صفحه {page} از {totalPages} ({data.length} ردیف)
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronRight size={14} />
              قبلی
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page === totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              بعدی
              <ChevronLeft size={14} />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
