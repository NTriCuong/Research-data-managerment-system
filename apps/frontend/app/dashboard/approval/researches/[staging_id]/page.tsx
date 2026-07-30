'use client'

import { referenceService, type StagingResearchObjectDetail } from '@/services/reference/reference.service'
import { approverService, type ApproveRequest } from '@/services/approver/approver.service'
import StagingDetailView from '@/components/data-entry/StagingDetailView'
import { parseAxiosError } from '@/lib/axios/error-paser'
import {
    ACCESS_LEVEL_LABEL,
    ACCESS_LEVEL_VALUES,
    isAccessLevelAllowed,
    WORKFLOW_STATUS_LABEL,
    WORKFLOW_STATUS_BADGE_CLASS,
} from '@/lib/constants/workflow'
import type { AccessLevel } from '@/services/data-entry/data-entry.service'
import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { ArrowLeft, Loader2 } from 'lucide-react'

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
    const [researchAccessLevel, setResearchAccessLevel] = useState<AccessLevel>('internal')
    const [fileAccessLevels, setFileAccessLevels] = useState<Record<string, AccessLevel>>({})
    const [rejectReason, setRejectReason] = useState('')
    const [submitting, setSubmitting] = useState(false)

    useEffect(() => {
        let cancelled = false

        Promise.all([
            referenceService.getMetadataByStagingId(stagingId),
            referenceService.getDepartments().catch(() => null),
            referenceService.getOutputTypes().catch(() => null),
        ])
            .then(([data, departments, outputTypes]) => {
                if (cancelled) return
                setDetail(data)
                setResearchAccessLevel(data.access_level)
                setFileAccessLevels(
                    Object.fromEntries(
                        data.files.map((file) => [
                            file.file_id,
                            isAccessLevelAllowed(file.access_level, data.access_level)
                                ? file.access_level
                                : data.access_level,
                        ])
                    )
                )
                if (departments) {
                    setDepartmentMap(
                        Object.fromEntries(
                            departments.items.map((department) => [
                                department.department_id,
                                department.department_name,
                            ])
                        )
                    )
                }
                if (outputTypes) {
                    setOutputTypeMap(
                        Object.fromEntries(
                            outputTypes.items.map((outputType) => [
                                outputType.output_type_id,
                                outputType.type_name,
                            ])
                        )
                    )
                }
            })
            .catch((err) => {
                if (!cancelled) setError(parseAxiosError(err).message)
            })
            .finally(() => {
                if (!cancelled) setLoading(false)
            })

        return () => {
            cancelled = true
        }
    }, [stagingId])

    const canAct = detail?.workflow_status === 'pending_approval'

    const handleOpenApproveModal = () => {
        if (detail) {
            setFileAccessLevels(
                Object.fromEntries(
                    detail.files.map((file) => [
                        file.file_id,
                        isAccessLevelAllowed(
                            fileAccessLevels[file.file_id] ?? file.access_level,
                            researchAccessLevel
                        )
                            ? fileAccessLevels[file.file_id] ?? file.access_level
                            : researchAccessLevel,
                    ])
                )
            )
        }
        setOpenApproveModal(true)
    }

    const handleApprove = async () => {
        if (!detail) return
        setSubmitting(true)
        try {
            const payload: ApproveRequest = {
                note: approveNote || undefined,
                access_level: researchAccessLevel,
                file_access_levels: detail.files.map((file) => ({
                    file_id: file.file_id,
                    access_level: fileAccessLevels[file.file_id] ?? file.access_level,
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

                        <p className="mt-4 text-sm font-medium text-gray-700">Ghi chú (không bắt buộc)</p>
                        <textarea
                            className="mt-2 w-full rounded-lg border p-2"
                            rows={3}
                            value={approveNote}
                            onChange={(e) => setApproveNote(e.target.value)}
                            placeholder="Nhập ghi chú..."
                        />

                        <div className="mt-5">
                            <label className="text-sm font-medium text-gray-700" htmlFor="research-access-level">
                                Quyền truy cập bài nghiên cứu
                            </label>
                            <select
                                id="research-access-level"
                                value={researchAccessLevel}
                                onChange={(event) => {
                                    const nextResearchAccessLevel = event.target.value as AccessLevel
                                    setResearchAccessLevel(nextResearchAccessLevel)
                                    setFileAccessLevels((current) =>
                                        Object.fromEntries(
                                            detail.files.map((file) => {
                                                const currentFileAccessLevel =
                                                    current[file.file_id] ?? file.access_level
                                                return [
                                                    file.file_id,
                                                    isAccessLevelAllowed(
                                                        currentFileAccessLevel,
                                                        nextResearchAccessLevel
                                                    )
                                                        ? currentFileAccessLevel
                                                        : nextResearchAccessLevel,
                                                ]
                                            })
                                        )
                                    )
                                }}
                                className="mt-2 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 focus:border-blue-500 focus:outline-none"
                            >
                                {ACCESS_LEVEL_VALUES.map((value) => (
                                    <option key={value} value={value}>{ACCESS_LEVEL_LABEL[value]}</option>
                                ))}
                            </select>
                        </div>

                        <div className="mt-5">
                            <p className="text-sm font-medium text-gray-700">Quyền truy cập tệp minh chứng</p>
                            <p className="mt-1 text-xs text-gray-500">
                                Chỉ tệp đặt là Công khai mới xuất hiện trên trang public.
                            </p>

                            <div className="mt-3 space-y-3">
                                {detail.files.length === 0 && (
                                    <p className="rounded-lg border border-gray-200 px-3 py-3 text-sm text-gray-400">
                                        Bản ghi không có tệp đính kèm.
                                    </p>
                                )}
                                {detail.files.map((file) => (
                                    <div
                                        key={file.file_id}
                                        className="flex flex-col gap-2 rounded-lg border border-gray-200 p-3 sm:flex-row sm:items-center sm:justify-between"
                                    >
                                        <div className="min-w-0">
                                            <p className="truncate text-sm font-medium text-gray-800">
                                                {file.original_filename}
                                            </p>
                                            <p className="text-xs text-gray-500">
                                                Quyền hiện tại: {ACCESS_LEVEL_LABEL[file.access_level] ?? file.access_level}
                                            </p>
                                        </div>
                                        <select
                                            value={fileAccessLevels[file.file_id] ?? file.access_level}
                                            onChange={(event) =>
                                                setFileAccessLevels((current) => ({
                                                    ...current,
                                                    [file.file_id]: event.target.value as AccessLevel,
                                                }))
                                            }
                                            className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 focus:border-blue-500 focus:outline-none"
                                        >
                                            {ACCESS_LEVEL_VALUES
                                                .filter((value) =>
                                                    isAccessLevelAllowed(value, researchAccessLevel)
                                                )
                                                .map((value) => (
                                                    <option key={value} value={value}>
                                                        {ACCESS_LEVEL_LABEL[value]}
                                                    </option>
                                                ))}
                                        </select>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="mt-5 flex justify-end gap-3">
                            <button
                                className="cursor-pointer rounded-lg border px-4 py-2"
                                onClick={() => setOpenApproveModal(false)}
                            >
                                Huỷ
                            </button>

                            <button
                                disabled={submitting}
                                className="flex cursor-pointer items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
                                onClick={handleApprove}
                            >
                                {submitting && <Loader2 size={14} className="animate-spin" />}
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
                                className="flex cursor-pointer items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-white disabled:opacity-50"
                                onClick={handleReject}
                            >
                                {submitting && <Loader2 size={14} className="animate-spin" />}
                                Xác nhận
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
