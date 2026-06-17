'use client'

import { dataEntryService, type StagingResearchObject } from '@/services/data-entry/data-entry.service'
import { referenceService } from '@/services/reference/reference.service'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

const WORKFLOW_STATUS_LABEL: Record<string, string> = {
    draft: 'Bản nháp',
    pending_review: 'Chờ kiểm duyệt',
    revision_required: 'Yêu cầu sửa lại',
    pending_approval: 'Chờ phê duyệt',
    approved: 'Đã duyệt',
    rejected: 'Bị từ chối',
}

const ACCESS_LEVEL_LABEL: Record<string, string> = {
    private: 'Riêng tư',
    internal: 'Nội bộ',
    public: 'Công khai',
}

function formatDateTime(value: string | null) {
    if (!value) return '-'
    return new Date(value).toLocaleString('vi-VN')
}

export default function Researches() {
    const router = useRouter()
    const [dataResearch, setDataResearch] = useState<StagingResearchObject[]>([])
    const [departmentMap, setDepartmentMap] = useState<Record<string, string>>({})
    const [outputTypeMap, setOutputTypeMap] = useState<Record<string, string>>({})
    const [userMap, setUserMap] = useState<Record<string, string>>({})
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        const fetchResearchData = async () => {
            setLoading(true)
            setError('')

            try {
                const data = await dataEntryService.getResearchData()
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

    return (
        <div className="p-6">
            <h1 className="mb-4 text-2xl font-bold">Researches</h1>

            {error && (
                <p className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-500">
                    {error}
                </p>
            )}

            {loading ? (
                <p className="text-sm text-gray-500">Đang tải dữ liệu...</p>
            ) : (
                <div className="max-h-[calc(100vh-180px)] overflow-auto rounded-lg border border-gray-200">
                    <table className="w-full min-w-max text-left text-sm whitespace-nowrap">
                        <thead className="sticky top-0 bg-gray-100 text-gray-600">
                            <tr>
                                <th className="px-4 py-3 font-medium">Staging ID</th>
                                <th className="px-4 py-3 font-medium">Tiêu đề</th>
                                <th className="px-4 py-3 font-medium">Loại sản phẩm</th>
                                <th className="px-4 py-3 font-medium">Đơn vị</th>
                                <th className="px-4 py-3 font-medium">Năm</th>
                                <th className="px-4 py-3 font-medium">Trạng thái</th>
                                <th className="px-4 py-3 font-medium">Mức truy cập</th>
                                <th className="px-4 py-3 font-medium">Source Research ID</th>
                                <th className="px-4 py-3 font-medium">Lý do cập nhật</th>
                                <th className="px-4 py-3 font-medium">Điểm chất lượng metadata</th>
                                <th className="px-4 py-3 font-medium">Người gửi</th>
                                <th className="px-4 py-3 font-medium">Ngày gửi</th>
                                <th className="px-4 py-3 font-medium">Ngày tạo</th>
                                <th className="px-4 py-3 font-medium">Ngày cập nhật</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {dataResearch.map((item) => (
                                <tr
                                    key={item.staging_id}
                                    onClick={() => router.push(`/dashboard/data-entry/update-metadata?staging_id=${item.staging_id}`)}
                                    className="cursor-pointer hover:bg-gray-50"
                                >
                                    <td className="max-w-40 truncate px-4 py-3" title={item.staging_id}>{item.staging_id}</td>
                                    <td className="px-4 py-3">{item.title}</td>
                                    <td className="px-4 py-3">{outputTypeMap[item.output_type_id] ?? item.output_type_id}</td>
                                    <td className="px-4 py-3">{departmentMap[item.department_id] ?? item.department_id}</td>
                                    <td className="px-4 py-3">{item.year ?? '-'}</td>
                                    <td className="px-4 py-3">{WORKFLOW_STATUS_LABEL[item.workflow_status] ?? item.workflow_status}</td>
                                    <td className="px-4 py-3">{ACCESS_LEVEL_LABEL[item.access_level] ?? item.access_level}</td>
                                    <td className="max-w-40 truncate px-4 py-3" title={item.source_core_research_id ?? undefined}>{item.source_core_research_id ?? '-'}</td>
                                    <td className="px-4 py-3">{item.update_reason ?? '-'}</td>
                                    <td className="max-w-40 truncate px-4 py-3" title={item.metadata_quality_score ?? undefined}>{item.metadata_quality_score ?? '-'}</td>
                                    <td className="max-w-40 truncate px-4 py-3" title={item.submitted_by ?? undefined}>
                                        {item.submitted_by ? (userMap[item.submitted_by] ?? item.submitted_by) : '-'}
                                    </td>
                                    <td className="px-4 py-3">{formatDateTime(item.submitted_at)}</td>
                                    <td className="px-4 py-3">{formatDateTime(item.created_at)}</td>
                                    <td className="px-4 py-3">{formatDateTime(item.updated_at)}</td>
                                </tr>
                            ))}

                            {dataResearch.length === 0 && (
                                <tr>
                                    <td colSpan={14} className="px-4 py-6 text-center text-gray-400">
                                        Không có dữ liệu
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    )
}
