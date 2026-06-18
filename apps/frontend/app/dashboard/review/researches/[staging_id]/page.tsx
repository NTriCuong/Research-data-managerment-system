'use client'

import { referenceService, type StagingResearchObjectDetail } from '@/services/reference/reference.service'
import { reviewerService } from '@/services/reviewer/reviewer.service'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { WORKFLOW_STATUS_LABEL, WORKFLOW_STATUS_BADGE_CLASS } from '@/lib/constants/workflow'
import StagingDetailView from '@/components/data-entry/StagingDetailView'
import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { ArrowLeft } from 'lucide-react'

function formatDateTime(value: string | null) {
    if (!value) return '-'
    return new Date(value).toLocaleString('vi-VN')
}

export default function ReviewResearchDetailPage() {
    const router = useRouter()
    const params = useParams<{ staging_id: string }>()
    const stagingId = params.staging_id

    const [detail, setDetail] = useState<StagingResearchObjectDetail | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    const [departmentMap, setDepartmentMap] = useState<Record<string, string>>({})
    const [outputTypeMap, setOutputTypeMap] = useState<Record<string, string>>({})

    const [openForwardModal, setOpenForwardModal] = useState(false)
    const [openRevisionModal, setOpenRevisionModal] = useState(false)
    const [forwardNote, setForwardNote] = useState('')
    const [revisionNote, setRevisionNote] = useState('')
    const [submitting, setSubmitting] = useState(false)

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

    useEffect(() => {
        fetchDetail()

        referenceService.getDepartments().then((res) => {
            setDepartmentMap(Object.fromEntries(res.items.map((d) => [d.department_id, d.department_name])))
        }).catch(() => null)

        referenceService.getOutputTypes().then((res) => {
            setOutputTypeMap(Object.fromEntries(res.items.map((o) => [o.output_type_id, o.type_name])))
        }).catch(() => null)
    }, [stagingId])

    const canReview = detail?.workflow_status === 'pending_review'

    const handleForward = async () => {
        setSubmitting(true)
        try {
            await reviewerService.forwardToApproval(stagingId, forwardNote || undefined)
            toast.success('Chuyển sang bước phê duyệt thành công')
            setOpenForwardModal(false)
            router.push('/dashboard/review/researches')
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setSubmitting(false)
        }
    }

    const handleRequestRevision = async () => {
        if (!revisionNote.trim()) {
            toast.error('Vui lòng nhập lý do yêu cầu chỉnh sửa')
            return
        }
        setSubmitting(true)
        try {
            await reviewerService.requestRevision(stagingId, revisionNote)
            toast.success('Đã gửi yêu cầu chỉnh sửa')
            setOpenRevisionModal(false)
            router.push('/dashboard/review/researches')
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setSubmitting(false)
        }
    }

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

    return (
        <div className="flex h-full flex-col bg-gray-50">
            <div className="flex-1 overflow-y-auto">
                <div className="mx-auto max-w-5xl space-y-6 p-6">
                    <div>
                        <button
                            type="button"
                            onClick={() => router.push('/dashboard/review/researches')}
                            className="mb-3 flex cursor-pointer items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700"
                        >
                            <ArrowLeft size={16} />
                            Quay lại danh sách
                        </button>

                        <div className="flex flex-wrap items-start justify-between gap-3">
                            <div>
                                <h1 className="text-2xl font-semibold text-gray-900">{detail.title}</h1>
                                <p className="mt-1 text-sm text-gray-500">
                                    Gửi lúc {formatDateTime(detail.submitted_at)}
                                    {detail.reviewed_at && ` · Xem xét lúc ${formatDateTime(detail.reviewed_at)}`}
                                </p>
                            </div>

                            <span className={`rounded-full px-3 py-1 text-sm font-medium ${WORKFLOW_STATUS_BADGE_CLASS[detail.workflow_status] ?? 'bg-gray-100 text-gray-700'}`}>
                                {WORKFLOW_STATUS_LABEL[detail.workflow_status] ?? detail.workflow_status}
                            </span>
                        </div>
                    </div>

                    <StagingDetailView detail={detail} departmentMap={departmentMap} outputTypeMap={outputTypeMap} />

                    {detail.revision_note && (
                        <div className="rounded-xl border border-amber-200 bg-amber-50 p-6">
                            <h2 className="mb-2 text-sm font-semibold text-amber-800">Ghi chú yêu cầu chỉnh sửa trước đó</h2>
                            <p className="text-sm text-amber-700">{detail.revision_note}</p>
                        </div>
                    )}
                </div>
            </div>

            <div className="border-t border-gray-200 bg-white px-6 py-4">
                <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3">
                    <p className="text-sm text-gray-500">
                        {canReview
                            ? 'Bản ghi đang chờ kiểm duyệt.'
                            : 'Bản ghi không ở trạng thái chờ kiểm duyệt nên không thể thực hiện hành động kiểm duyệt.'}
                    </p>

                    <div className="flex justify-end gap-3">
                        <button
                            type="button"
                            disabled={!canReview}
                            onClick={() => setOpenRevisionModal(true)}
                            className="cursor-pointer rounded-lg border border-red-300 px-5 py-2 text-sm font-medium text-red-600 disabled:cursor-not-allowed disabled:opacity-40"
                        >
                            Yêu cầu chỉnh sửa
                        </button>

                        <button
                            type="button"
                            disabled={!canReview}
                            onClick={() => setOpenForwardModal(true)}
                            className="cursor-pointer rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-gray-300"
                        >
                            Chuyển chờ sang phê duyệt
                        </button>
                    </div>
                </div>
            </div>

            {openForwardModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
                    <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
                        <h2 className="text-lg font-semibold">Chuyển bản ghi sang bước phê duyệt</h2>

                        <p className="mt-2 text-sm text-gray-500">Ghi chú (không bắt buộc)</p>

                        <textarea
                            className="mt-4 w-full rounded-lg border p-2"
                            rows={4}
                            value={forwardNote}
                            onChange={(e) => setForwardNote(e.target.value)}
                            placeholder="Nhập ghi chú..."
                        />

                        <div className="mt-5 flex justify-end gap-3">
                            <button
                                className="cursor-pointer rounded-lg border px-4 py-2"
                                onClick={() => setOpenForwardModal(false)}
                            >
                                Huỷ
                            </button>

                            <button
                                disabled={submitting}
                                className="cursor-pointer rounded-lg bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
                                onClick={handleForward}
                            >
                                Xác nhận
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {openRevisionModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
                    <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
                        <h2 className="text-lg font-semibold">Yêu cầu chỉnh sửa</h2>

                        <p className="mt-2 text-sm text-gray-500">Lý do yêu cầu chỉnh sửa (bắt buộc)</p>

                        <textarea
                            className="mt-4 w-full rounded-lg border p-2"
                            rows={4}
                            value={revisionNote}
                            onChange={(e) => setRevisionNote(e.target.value)}
                            placeholder="Nhập lý do..."
                        />

                        <div className="mt-5 flex justify-end gap-3">
                            <button
                                className="cursor-pointer rounded-lg border px-4 py-2"
                                onClick={() => setOpenRevisionModal(false)}
                            >
                                Huỷ
                            </button>

                            <button
                                disabled={submitting}
                                className="cursor-pointer rounded-lg bg-red-600 px-4 py-2 text-white disabled:opacity-50"
                                onClick={handleRequestRevision}
                            >
                                Xác nhận
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
