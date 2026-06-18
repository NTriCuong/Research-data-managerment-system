'use client'

import { referenceService, type StagingResearchObjectDetail } from '@/services/reference/reference.service'
import { approverService, type ApproveRequest } from '@/services/approver/approver.service'
import StagingDetailView from '@/components/data-entry/StagingDetailView'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { WORKFLOW_STATUS_LABEL, WORKFLOW_STATUS_BADGE_CLASS } from '@/lib/constants/workflow'
import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { ArrowLeft } from 'lucide-react'

type AccessLevel = "private" | "internal" | "public"

const ACCESS_LEVEL_OPTIONS: { value: AccessLevel; label: string }[] = [
    { value: 'private', label: 'Riêng tư (Private)' },
    { value: 'internal', label: 'Nội bộ (Internal)' },
    { value: 'public', label: 'Công khai (Public)' },
]

function formatDateTime(value: string | null) {
    if (!value) return '-'
    return new Date(value).toLocaleString('vi-VN')
}

export default function ApprovalResearchDetailPage() {
    const router = useRouter()
    const params = useParams<{ staging_id: string }>()
    const stagingId = params.staging_id

    const [detail, setDetail] = useState<StagingResearchObjectDetail | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    const [departmentMap, setDepartmentMap] = useState<Record<string, string>>({})
    const [outputTypeMap, setOutputTypeMap] = useState<Record<string, string>>({})

    const [openApproveModal, setOpenApproveModal] = useState(false)
    const [openRejectModal, setOpenRejectModal] = useState(false)
    const [approveNote, setApproveNote] = useState('')
    const [approveAccessLevel, setApproveAccessLevel] = useState<AccessLevel>('private')
    const [fileAccessLevels, setFileAccessLevels] = useState<Record<string, AccessLevel>>({})
    const [rejectReason, setRejectReason] = useState('')
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

    const canAct = detail?.workflow_status === 'pending_approval'

    const handleOpenApproveModal = () => {
        if (detail) {
            setFileAccessLevels(Object.fromEntries(detail.files.map((f) => [f.file_id, approveAccessLevel])))
        }
        setOpenApproveModal(true)
    }

    const handleApplyAccessLevelToAllFiles = () => {
        if (!detail) return
        setFileAccessLevels(Object.fromEntries(detail.files.map((f) => [f.file_id, approveAccessLevel])))
    }

    const handleApprove = async () => {
        if (!detail) return
        setSubmitting(true)
        try {
            const payload: ApproveRequest = {
                note: approveNote || undefined,
                access_level: approveAccessLevel,
                file_access_levels: detail.files.map((f) => ({
                    file_id: f.file_id,
                    access_level: fileAccessLevels[f.file_id] ?? approveAccessLevel,
                })),
            }
            await approverService.approveRecord(stagingId, payload)
            toast.success('Phê duyệt và xuất bản vào core thành công')
            setOpenApproveModal(false)
            router.push('/dashboard/approval/researches')
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setSubmitting(false)
        }
    }

    const handleReject = async () => {
        if (!rejectReason.trim()) {
            toast.error('Vui lòng nhập lý do từ chối')
            return
        }
        setSubmitting(true)
        try {
            await approverService.rejectRecord(stagingId, rejectReason)
            toast.success('Đã từ chối bản ghi')
            setOpenRejectModal(false)
            router.push('/dashboard/approval/researches')
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
                            onClick={() => router.push('/dashboard/approval/researches')}
                            className="mb-3 flex cursor-pointer items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700"
                        >
                            <ArrowLeft size={16} />
                            Quay lại danh sách
                        </button>

                        <div className="flex flex-wrap items-start justify-between gap-3">
                            <div className="min-w-0">
                                <h1 className="wrap-break-word text-2xl font-semibold text-gray-900">{detail.title}</h1>
                                <p className="mt-1 text-sm text-gray-500">
                                    Gửi lúc {formatDateTime(detail.submitted_at)}
                                    {detail.reviewed_at && ` · Kiểm duyệt lúc ${formatDateTime(detail.reviewed_at)}`}
                                </p>
                            </div>

                            <span className={`rounded-full px-3 py-1 text-sm font-medium ${WORKFLOW_STATUS_BADGE_CLASS[detail.workflow_status] ?? 'bg-gray-100 text-gray-700'}`}>
                                {WORKFLOW_STATUS_LABEL[detail.workflow_status] ?? detail.workflow_status}
                            </span>
                        </div>
                    </div>

                    <StagingDetailView detail={detail} departmentMap={departmentMap} outputTypeMap={outputTypeMap} />
                </div>
            </div>

            <div className="border-t border-gray-200 bg-white px-6 py-4">
                <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3">
                    <p className="text-sm text-gray-500">
                        {canAct
                            ? 'Bản ghi đang chờ phê duyệt.'
                            : 'Bản ghi không ở trạng thái chờ phê duyệt nên không thể thực hiện hành động này.'}
                    </p>

                    <div className="flex justify-end gap-3">
                        <button
                            type="button"
                            disabled={!canAct}
                            onClick={() => setOpenRejectModal(true)}
                            className="cursor-pointer rounded-lg border border-red-300 px-5 py-2 text-sm font-medium text-red-600 disabled:cursor-not-allowed disabled:opacity-40"
                        >
                            Từ chối
                        </button>

                        <button
                            type="button"
                            disabled={!canAct}
                            onClick={handleOpenApproveModal}
                            className="cursor-pointer rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-gray-300"
                        >
                            Duyệt vào core
                        </button>
                    </div>
                </div>
            </div>

            {openApproveModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
                    <div className="max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-lg bg-white p-6 shadow-lg">
                        <h2 className="text-lg font-semibold">Duyệt bản ghi vào core</h2>

                        <p className="mt-4 text-sm font-medium text-gray-700">Mức truy cập chung (Access Level)</p>
                        <select
                            className="mt-2 w-full rounded-lg border px-3 py-2 text-sm"
                            value={approveAccessLevel}
                            onChange={(e) => setApproveAccessLevel(e.target.value as AccessLevel)}
                        >
                            {ACCESS_LEVEL_OPTIONS.map((opt) => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                        </select>

                        {detail.files.length > 0 && (
                            <div className="mt-4">
                                <div className="flex items-center justify-between">
                                    <p className="text-sm font-medium text-gray-700">Mức truy cập theo tệp</p>
                                    <button
                                        type="button"
                                        onClick={handleApplyAccessLevelToAllFiles}
                                        className="cursor-pointer text-xs text-blue-600 hover:underline"
                                    >
                                        Áp dụng mức chung cho tất cả
                                    </button>
                                </div>

                                <ul className="mt-2 divide-y divide-gray-100 rounded-lg border border-gray-100">
                                    {detail.files.map((file) => (
                                        <li key={file.file_id} className="flex items-center justify-between gap-3 px-3 py-2">
                                            <span className="truncate text-sm text-gray-800">{file.original_filename}</span>
                                            <select
                                                className="rounded-md border px-2 py-1 text-xs"
                                                value={fileAccessLevels[file.file_id] ?? approveAccessLevel}
                                                onChange={(e) =>
                                                    setFileAccessLevels((prev) => ({
                                                        ...prev,
                                                        [file.file_id]: e.target.value as AccessLevel,
                                                    }))
                                                }
                                            >
                                                {ACCESS_LEVEL_OPTIONS.map((opt) => (
                                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                                ))}
                                            </select>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        <p className="mt-4 text-sm font-medium text-gray-700">Ghi chú (không bắt buộc)</p>
                        <textarea
                            className="mt-2 w-full rounded-lg border p-2"
                            rows={3}
                            value={approveNote}
                            onChange={(e) => setApproveNote(e.target.value)}
                            placeholder="Nhập ghi chú..."
                        />

                        <div className="mt-5 flex justify-end gap-3">
                            <button
                                className="cursor-pointer rounded-lg border px-4 py-2"
                                onClick={() => setOpenApproveModal(false)}
                            >
                                Huỷ
                            </button>

                            <button
                                disabled={submitting}
                                className="cursor-pointer rounded-lg bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
                                onClick={handleApprove}
                            >
                                Xác nhận duyệt
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {openRejectModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
                    <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
                        <h2 className="text-lg font-semibold">Từ chối bản ghi</h2>

                        <p className="mt-2 text-sm text-gray-500">Lý do từ chối (bắt buộc)</p>

                        <textarea
                            className="mt-4 w-full rounded-lg border p-2"
                            rows={4}
                            value={rejectReason}
                            onChange={(e) => setRejectReason(e.target.value)}
                            placeholder="Nhập lý do..."
                        />

                        <div className="mt-5 flex justify-end gap-3">
                            <button
                                className="cursor-pointer rounded-lg border px-4 py-2"
                                onClick={() => setOpenRejectModal(false)}
                            >
                                Huỷ
                            </button>

                            <button
                                disabled={submitting}
                                className="cursor-pointer rounded-lg bg-red-600 px-4 py-2 text-white disabled:opacity-50"
                                onClick={handleReject}
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
