'use client'

import { referenceService, type StagingResearchObjectDetail } from '@/services/reference/reference.service'
import FormMetadata from '@/components/data-entry/Form-metadata'
import StagingDetailView from '@/components/data-entry/StagingDetailView'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { WORKFLOW_STATUS_LABEL, WORKFLOW_STATUS_BADGE_CLASS } from '@/lib/constants/workflow'
import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { ArrowLeft, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from '@/components/ui/alert-dialog'

const EDITABLE_STATUSES = ['draft', 'revision_required']

export default function DataEntryResearchDetailPage() {
    const router = useRouter()
    const params = useParams<{ staging_id: string }>()
    const stagingId = params.staging_id

    const [detail, setDetail] = useState<StagingResearchObjectDetail | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
    const [deleting, setDeleting] = useState(false)

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

    const handleDeleteDraft = async () => {
        setDeleting(true)
        try {
            await referenceService.deleteDraft(stagingId)
            toast.success('Xóa bản nháp thành công')
            setDeleteDialogOpen(false)
            router.push('/dashboard/data-entry/researches')
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setDeleting(false)
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

    const isEditable = EDITABLE_STATUSES.includes(detail.workflow_status)

    return (
        <div className="min-h-full bg-gray-50">
            <div className="mx-auto max-w-5xl space-y-6 p-6">
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
                        <h1 className="min-w-0 wrap-break-word text-2xl font-semibold text-gray-900">{detail.title || 'Bản ghi nghiên cứu'}</h1>

                        <div className="flex items-center gap-2">
                            {detail.workflow_status === 'draft' && (
                                <Button variant="destructive" onClick={() => setDeleteDialogOpen(true)}>
                                    <Trash2 />
                                    Xóa bản nháp
                                </Button>
                            )}

                            <span className={`rounded-full px-3 py-1 text-sm font-medium ${WORKFLOW_STATUS_BADGE_CLASS[detail.workflow_status] ?? 'bg-gray-100 text-gray-700'}`}>
                                {WORKFLOW_STATUS_LABEL[detail.workflow_status] ?? detail.workflow_status}
                            </span>
                        </div>
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

            <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Xóa bản nháp này?</AlertDialogTitle>
                        <AlertDialogDescription>
                            Bản nháp <span className="font-medium">{detail.title || 'Bản ghi nghiên cứu'}</span> sẽ bị xóa. Hành động này không thể hoàn tác.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel disabled={deleting}>Hủy</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={(event) => {
                                event.preventDefault()
                                void handleDeleteDraft()
                            }}
                            disabled={deleting}
                            variant="destructive"
                        >
                            {deleting ? 'Đang xóa...' : 'Xóa bản nháp'}
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    )
}
