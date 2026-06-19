'use client'

import { type StagingResearchObject } from '@/services/data-entry/data-entry.service'
import { reviewerService } from '@/services/reviewer/reviewer.service'
import { referenceService } from '@/services/reference/reference.service'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { WORKFLOW_STATUS_LABEL, WORKFLOW_STATUS_BADGE_CLASS, ACCESS_LEVEL_LABEL, ACCESS_LEVEL_BADGE_CLASS } from '@/lib/constants/workflow'
import { useRouter } from 'next/navigation'
import { useEffect, useMemo, useState } from 'react'
import { Search } from 'lucide-react'

function formatDateTime(value: string | null) {
    if (!value) return '-'
    return new Date(value).toLocaleString('vi-VN')
}

export default function Researches() {
    const router = useRouter()
    const [dataResearch, setDataResearch] = useState<StagingResearchObject[]>([])
    const [departmentMap, setDepartmentMap] = useState<Record<string, string>>({})
    const [outputTypeMap, setOutputTypeMap] = useState<Record<string, string>>({})
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [search, setSearch] = useState('')

    useEffect(() => {
        const fetchResearchData = async () => {
            setLoading(true)
            setError('')

            try {
                const data = await reviewerService.getPendingReviews()
                setDataResearch(data)
            } catch (err) {
                setError(parseAxiosError(err).message)
            }

            const [departments, outputTypes] = await Promise.all([
                referenceService.getDepartments().catch(() => null),
                referenceService.getOutputTypes().catch(() => null),
            ])

            if (departments) {
                setDepartmentMap(Object.fromEntries(departments.items.map((d) => [d.department_id, d.department_name])))
            }
            if (outputTypes) {
                setOutputTypeMap(Object.fromEntries(outputTypes.items.map((o) => [o.output_type_id, o.type_name])))
            }

            setLoading(false)
        }

        fetchResearchData()
    }, [])

    const filteredData = useMemo(() => {
        const q = search.trim().toLowerCase()
        if (!q) return dataResearch
        return dataResearch.filter((item) => item.title.toLowerCase().includes(q))
    }, [dataResearch, search])

    return (
        <div className="space-y-6 p-6">
            <div className="flex flex-wrap items-end justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900">Nghiên cứu chờ kiểm duyệt</h1>
                    <p className="mt-1 text-sm text-gray-500">
                        {dataResearch.length} bản ghi đang chờ kiểm duyệt
                    </p>
                </div>

                <div className="relative">
                    <Search size={16} className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-gray-400" />
                    <input
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Tìm theo tiêu đề..."
                        className="w-64 rounded-lg border border-gray-200 py-2 pl-9 pr-3 text-sm focus:border-blue-400 focus:outline-none"
                    />
                </div>
            </div>

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-500">
                    {error}
                </p>
            )}

            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                <div className="max-h-[calc(100vh-260px)] overflow-auto">
                    <table className="w-full min-w-max text-left text-sm whitespace-nowrap">
                        <thead className="sticky top-0 bg-gray-50 text-xs font-semibold uppercase tracking-wide text-gray-500">
                            <tr>
                                <th className="px-4 py-3">Tiêu đề</th>
                                <th className="px-4 py-3">Loại sản phẩm</th>
                                <th className="px-4 py-3">Đơn vị</th>
                                <th className="px-4 py-3">Năm</th>
                                <th className="px-4 py-3">Trạng thái</th>
                                <th className="px-4 py-3">Mức truy cập</th>
                                <th className="px-4 py-3">Điểm chất lượng</th>
                                <th className="px-4 py-3">Ngày gửi</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {loading && (
                                <tr>
                                    <td colSpan={8} className="px-4 py-6 text-center text-sm text-gray-400">
                                        Đang tải dữ liệu...
                                    </td>
                                </tr>
                            )}

                            {!loading && filteredData.map((item) => (
                                <tr
                                    key={item.staging_id}
                                    onClick={() => router.push(`/dashboard/review/researches/${item.staging_id}`)}
                                    className="cursor-pointer transition hover:bg-blue-50/60"
                                >
                                    <td className="max-w-80 truncate px-4 py-3 font-medium text-gray-900" title={item.title}>{item.title}</td>
                                    <td className="px-4 py-3 text-gray-600">{outputTypeMap[item.output_type_id] ?? '-'}</td>
                                    <td className="px-4 py-3 text-gray-600">{departmentMap[item.department_id] ?? '-'}</td>
                                    <td className="px-4 py-3 text-gray-600">{item.year ?? '-'}</td>
                                    <td className="px-4 py-3">
                                        <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${WORKFLOW_STATUS_BADGE_CLASS[item.workflow_status] ?? 'bg-gray-100 text-gray-700'}`}>
                                            {WORKFLOW_STATUS_LABEL[item.workflow_status] ?? item.workflow_status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${ACCESS_LEVEL_BADGE_CLASS[item.access_level] ?? 'bg-gray-100 text-gray-700'}`}>
                                            {ACCESS_LEVEL_LABEL[item.access_level] ?? item.access_level}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-gray-600">{item.metadata_quality_score ?? '-'}</td>
                                    <td className="px-4 py-3 text-gray-600">{formatDateTime(item.submitted_at)}</td>
                                </tr>
                            ))}

                            {!loading && filteredData.length === 0 && (
                                <tr>
                                    <td colSpan={8} className="px-4 py-10 text-center text-sm text-gray-400">
                                        Không có dữ liệu
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
