'use client'

import { referenceService, type StagingResearchObjectDetail } from '@/services/reference/reference.service'
import FormMetadata from '@/components/data-entry/Form-metadata'
import StagingDetailView from '@/components/data-entry/StagingDetailView'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { WORKFLOW_STATUS_LABEL, WORKFLOW_STATUS_BADGE_CLASS } from '@/lib/constants/workflow'
import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { ArrowLeft } from 'lucide-react'

const EDITABLE_STATUSES = ['draft', 'revision_required']

export default function DataEntryResearchDetailPage() {
    const router = useRouter()
    const params = useParams<{ staging_id: string }>()
    const stagingId = params.staging_id

    const [detail, setDetail] = useState<StagingResearchObjectDetail | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    const [departmentMap, setDepartmentMap] = useState<Record<string, string>>({})
    const [outputTypeMap, setOutputTypeMap] = useState<Record<string, string>>({})

    useEffect(() => {
        const fetchDetail = async () => {
            setLoading(true)
            setError('')
            try {
                const data = await referenceService.getMetadataByStagingId(stagingId)
                setDetail(data)
            } catch (err) {
                setError(parseAxiosError(err).message)
            }
            setLoading(false)
        }

        fetchDetail()

        referenceService.getDepartments().then((res) => {
            setDepartmentMap(Object.fromEntries(res.items.map((d) => [d.department_id, d.department_name])))
        }).catch(() => null)

        referenceService.getOutputTypes().then((res) => {
            setOutputTypeMap(Object.fromEntries(res.items.map((o) => [o.output_type_id, o.type_name])))
        }).catch(() => null)
    }, [stagingId])

    if (loading) {
        return (
            <div className="flex h-full items-center justify-center p-6">
                <p className="text-sm text-gray-500">Đang tải dữ liệu...</p>
            </div>
        )
    }

    if (error || !detail) {
        return (
            <div className="p-6">
                <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-500">
                    {error || 'Không tìm thấy bản ghi'}
                </p>
            </div>
        )
    }

    const isEditable = EDITABLE_STATUSES.includes(detail.workflow_status)

    return (
        <div className="min-h-full bg-gray-50">
            <div className="mx-auto max-w-7xl space-y-6 p-6">
                <div>
                    <button
                        type="button"
                        onClick={() => router.push('/dashboard/data-entry/researches')}
                        className="mb-3 flex cursor-pointer items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700"
                    >
                        <ArrowLeft size={16} />
                        Quay lại danh sách
                    </button>

                    <div className="flex flex-wrap items-center justify-between gap-3">
                        <h1 className="text-2xl font-semibold text-gray-900">{detail.title || 'Bản ghi nghiên cứu'}</h1>

                        <span className={`rounded-full px-3 py-1 text-sm font-medium ${WORKFLOW_STATUS_BADGE_CLASS[detail.workflow_status] ?? 'bg-gray-100 text-gray-700'}`}>
                            {WORKFLOW_STATUS_LABEL[detail.workflow_status] ?? detail.workflow_status}
                        </span>
                    </div>
                </div>

                {detail.revision_note && (
                    <div className="rounded-xl border border-amber-200 bg-amber-50 p-6">
                        <h2 className="mb-2 text-sm font-semibold text-amber-800">Yêu cầu chỉnh sửa từ người kiểm duyệt</h2>
                        <p className="text-sm text-amber-700">{detail.revision_note}</p>
                    </div>
                )}

                {detail.rejection_reason && (
                    <div className="rounded-xl border border-red-200 bg-red-50 p-6">
                        <h2 className="mb-2 text-sm font-semibold text-red-800">Lý do từ chối</h2>
                        <p className="text-sm text-red-700">{detail.rejection_reason}</p>
                    </div>
                )}

                {!isEditable && (
                    <StagingDetailView detail={detail} departmentMap={departmentMap} outputTypeMap={outputTypeMap} />
                )}
            </div>

            {isEditable && (
                <FormMetadata stagingId={stagingId} initialDetail={detail} />
            )}
        </div>
    )
}
