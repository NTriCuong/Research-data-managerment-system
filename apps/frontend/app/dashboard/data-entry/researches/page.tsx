'use client'

import { useEffect, useMemo, useState } from 'react'
import { FilePenLine, Loader2 } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

import FilterToolbar, { type FilterSelect } from '@/components/dashboard/filter-toolbar'
import { Button } from '@/components/ui/button'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import { RtlPagination } from '@/components/ui/rtl-pagination'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { Textarea } from '@/components/ui/textarea'
import { parseAxiosError } from '@/lib/axios/error-paser'
import {
    ACCESS_LEVEL_BADGE_CLASS,
    ACCESS_LEVEL_LABEL,
    WORKFLOW_STATUS_BADGE_CLASS,
    WORKFLOW_STATUS_LABEL,
} from '@/lib/constants/workflow'
import { coreRepositoryService, type CoreResearchObject } from '@/services/core/core-repository.service'
import { dataEntryService, type StagingResearchObject } from '@/services/data-entry/data-entry.service'
import { referenceService } from '@/services/reference/reference.service'

const PAGE_SIZE = 10
const ACTIVE_REVISION_STATUSES = new Set([
    'draft',
    'pending_review',
    'revision_required',
    'pending_approval',
])

type ResearchTab = 'pending' | 'published'

function formatDateTime(value: string | null) {
    if (!value) return '-'
    return new Date(value).toLocaleString('vi-VN')
}

export default function Researches() {
    const router = useRouter()
    const [activeTab, setActiveTab] = useState<ResearchTab>('pending')
    const [stagingResearches, setStagingResearches] = useState<StagingResearchObject[]>([])
    const [publishedResearches, setPublishedResearches] = useState<CoreResearchObject[]>([])
    const [departmentMap, setDepartmentMap] = useState<Record<string, string>>({})
    const [outputTypeMap, setOutputTypeMap] = useState<Record<string, string>>({})
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [search, setSearch] = useState('')
    const [departmentFilter, setDepartmentFilter] = useState('')
    const [outputTypeFilter, setOutputTypeFilter] = useState('')
    const [statusFilter, setStatusFilter] = useState('')
    const [accessFilter, setAccessFilter] = useState('')
    const [yearFilter, setYearFilter] = useState('')
    const [page, setPage] = useState(1)
    const [revisionTarget, setRevisionTarget] = useState<CoreResearchObject | null>(null)
    const [updateReason, setUpdateReason] = useState('')
    const [creatingRevision, setCreatingRevision] = useState(false)

    useEffect(() => {
        const fetchResearchData = async () => {
            setLoading(true)
            setError('')

            try {
                const [staging, published] = await Promise.all([
                    dataEntryService.getResearchData(),
                    coreRepositoryService.listMyCoreRecords(),
                ])
                setStagingResearches(staging)
                setPublishedResearches(published)
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

        void fetchResearchData()
    }, [])

    const pendingResearches = useMemo(
        () => stagingResearches.filter((item) => item.workflow_status !== 'approved'),
        [stagingResearches]
    )

    const activeRevisionByCore = useMemo(() => {
        const revisions = new Map<string, StagingResearchObject>()
        stagingResearches.forEach((item) => {
            if (
                item.source_core_research_id &&
                ACTIVE_REVISION_STATUSES.has(item.workflow_status)
            ) {
                revisions.set(item.source_core_research_id, item)
            }
        })
        return revisions
    }, [stagingResearches])

    const filteredPendingResearches = useMemo(() => {
        const q = search.trim().toLowerCase()
        return pendingResearches.filter((item) => {
            const matchesSearch =
                !q ||
                item.title.toLowerCase().includes(q) ||
                item.staging_id.toLowerCase().includes(q)
            const matchesDepartment = !departmentFilter || item.department_id === departmentFilter
            const matchesOutputType = !outputTypeFilter || item.output_type_id === outputTypeFilter
            const matchesStatus = !statusFilter || item.workflow_status === statusFilter
            const matchesAccess = !accessFilter || item.access_level === accessFilter
            const matchesYear = !yearFilter || String(item.year ?? '') === yearFilter

            return matchesSearch && matchesDepartment && matchesOutputType && matchesStatus && matchesAccess && matchesYear
        })
    }, [
        accessFilter,
        departmentFilter,
        outputTypeFilter,
        pendingResearches,
        search,
        statusFilter,
        yearFilter,
    ])

    const filteredPublishedResearches = useMemo(() => {
        const q = search.trim().toLowerCase()
        return publishedResearches.filter((item) => {
            const matchesSearch =
                !q ||
                item.title.toLowerCase().includes(q) ||
                item.research_id.toLowerCase().includes(q)
            const matchesDepartment = !departmentFilter || item.department_id === departmentFilter
            const matchesOutputType = !outputTypeFilter || item.output_type_id === outputTypeFilter
            const matchesAccess = !accessFilter || item.access_level === accessFilter
            const matchesYear = !yearFilter || String(item.year ?? '') === yearFilter

            return matchesSearch && matchesDepartment && matchesOutputType && matchesAccess && matchesYear
        })
    }, [
        accessFilter,
        departmentFilter,
        outputTypeFilter,
        publishedResearches,
        search,
        yearFilter,
    ])

    const yearOptions = useMemo(() => {
        const years = activeTab === 'pending'
            ? pendingResearches.map((item) => item.year)
            : publishedResearches.map((item) => item.year)

        return Array.from(new Set(years.filter((year): year is number => year !== null)))
            .sort((a, b) => b - a)
            .map((year) => ({ value: String(year), label: String(year) }))
    }, [activeTab, pendingResearches, publishedResearches])

    const activeFilteredCount = activeTab === 'pending'
        ? filteredPendingResearches.length
        : filteredPublishedResearches.length
    const totalPages = Math.max(1, Math.ceil(activeFilteredCount / PAGE_SIZE))
    const currentPage = Math.min(page, totalPages)
    const paginatedPendingResearches = useMemo(
        () => filteredPendingResearches.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE),
        [currentPage, filteredPendingResearches]
    )
    const paginatedPublishedResearches = useMemo(
        () => filteredPublishedResearches.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE),
        [currentPage, filteredPublishedResearches]
    )

    const filterSelects: FilterSelect[] = [
        {
            key: 'output-type',
            label: 'Loại sản phẩm',
            value: outputTypeFilter,
            allLabel: 'Tất cả loại',
            options: Object.entries(outputTypeMap).map(([value, label]) => ({ value, label })),
            onChange: (value) => {
                setOutputTypeFilter(value)
                setPage(1)
            },
        },
        {
            key: 'department',
            label: 'Đơn vị',
            value: departmentFilter,
            allLabel: 'Tất cả đơn vị',
            options: Object.entries(departmentMap).map(([value, label]) => ({ value, label })),
            onChange: (value) => {
                setDepartmentFilter(value)
                setPage(1)
            },
        },
        ...(activeTab === 'pending'
            ? [{
                key: 'status',
                label: 'Trạng thái',
                value: statusFilter,
                allLabel: 'Tất cả trạng thái',
                options: Object.entries(WORKFLOW_STATUS_LABEL)
                    .filter(([value]) => value !== 'approved')
                    .map(([value, label]) => ({ value, label })),
                onChange: (value: string) => {
                    setStatusFilter(value)
                    setPage(1)
                },
            }]
            : []),
        {
            key: 'access',
            label: 'Mức truy cập',
            value: accessFilter,
            allLabel: 'Tất cả mức',
            options: Object.entries(ACCESS_LEVEL_LABEL).map(([value, label]) => ({ value, label })),
            onChange: (value) => {
                setAccessFilter(value)
                setPage(1)
            },
        },
        {
            key: 'year',
            label: 'Năm',
            value: yearFilter,
            allLabel: 'Tất cả năm',
            options: yearOptions,
            onChange: (value) => {
                setYearFilter(value)
                setPage(1)
            },
        },
    ]

    const resetFilters = () => {
        setSearch('')
        setDepartmentFilter('')
        setOutputTypeFilter('')
        setStatusFilter('')
        setAccessFilter('')
        setYearFilter('')
        setPage(1)
    }

    const switchTab = (tab: ResearchTab) => {
        setActiveTab(tab)
        setStatusFilter('')
        setPage(1)
    }

    const openRevisionDialog = (research: CoreResearchObject) => {
        setRevisionTarget(research)
        setUpdateReason('')
    }

    const handleCreateRevision = async () => {
        const reason = updateReason.trim()
        if (!revisionTarget || !reason) return

        setCreatingRevision(true)
        try {
            const revision = await dataEntryService.createRevision(revisionTarget.research_id, reason)
            toast.success('Đã kéo nghiên cứu về bản nháp để cập nhật')
            setRevisionTarget(null)
            router.push(`/dashboard/data-entry/researches/${revision.staging_id}`)
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setCreatingRevision(false)
        }
    }

    return (
        <div className="space-y-6 p-6">
            <div>
                <h1 className="text-2xl font-semibold text-gray-900">Nghiên cứu của bạn</h1>
                <p className="mt-1 text-sm text-gray-500">
                    Tôn vinh và ủng hộ những đóng góp trong quá khứ, hiện tại và tương lai của bạn.
                </p>
            </div>

            <div className="flex w-fit rounded-xl border border-gray-200 bg-gray-50 p-1" role="tablist" aria-label="Nhóm nghiên cứu">
                <button
                    type="button"
                    role="tab"
                    aria-selected={activeTab === 'pending'}
                    onClick={() => switchTab('pending')}
                    className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                        activeTab === 'pending'
                            ? 'bg-white text-blue-700 shadow-sm'
                            : 'text-gray-500 hover:text-gray-800'
                    }`}
                >
                    Chờ duyệt
                    <span className="ml-2 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                        {pendingResearches.length}
                    </span>
                </button>
                <button
                    type="button"
                    role="tab"
                    aria-selected={activeTab === 'published'}
                    onClick={() => switchTab('published')}
                    className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                        activeTab === 'published'
                            ? 'bg-white text-blue-700 shadow-sm'
                            : 'text-gray-500 hover:text-gray-800'
                    }`}
                >
                    Đã công bố
                    <span className="ml-2 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                        {publishedResearches.length}
                    </span>
                </button>
            </div>

            <FilterToolbar
                search={search}
                onSearchChange={(value) => {
                    setSearch(value)
                    setPage(1)
                }}
                searchPlaceholder="Tìm theo tiêu đề hoặc mã nghiên cứu..."
                selects={filterSelects}
                resultCount={activeFilteredCount}
                onReset={resetFilters}
            />

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-500">
                    {error}
                </p>
            )}

            {activeTab === 'pending' ? (
                <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                    <div className="max-h-[calc(100vh-320px)] overflow-auto">
                        <Table className="min-w-max">
                            <TableHeader className="sticky top-0 z-10 bg-gray-50 text-xs uppercase tracking-wide text-gray-500">
                                <TableRow className="hover:bg-transparent">
                                    <TableHead className="px-4 py-3">Tiêu đề</TableHead>
                                    <TableHead className="px-4 py-3">Loại sản phẩm</TableHead>
                                    <TableHead className="px-4 py-3">Đơn vị</TableHead>
                                    <TableHead className="px-4 py-3">Năm</TableHead>
                                    <TableHead className="px-4 py-3">Trạng thái</TableHead>
                                    <TableHead className="px-4 py-3">Mức truy cập</TableHead>
                                    <TableHead className="px-4 py-3">Loại hồ sơ</TableHead>
                                    <TableHead className="px-4 py-3">Lý do cập nhật</TableHead>
                                    <TableHead className="px-4 py-3">Điểm chất lượng</TableHead>
                                    <TableHead className="px-4 py-3">Ngày cập nhật</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {loading && (
                                    <TableRow>
                                        <TableCell colSpan={10} className="px-4 py-6 text-center text-sm text-gray-400">
                                            Đang tải dữ liệu...
                                        </TableCell>
                                    </TableRow>
                                )}

                                {!loading && paginatedPendingResearches.map((item) => (
                                    <TableRow
                                        key={item.staging_id}
                                        onClick={() => router.push(`/dashboard/data-entry/researches/${item.staging_id}`)}
                                        className="cursor-pointer transition hover:bg-blue-50/60"
                                    >
                                        <TableCell className="max-w-80 truncate px-4 py-3 font-medium text-gray-900" title={item.title}>
                                            {item.title}
                                        </TableCell>
                                        <TableCell className="px-4 py-3 text-gray-600">{outputTypeMap[item.output_type_id] ?? '-'}</TableCell>
                                        <TableCell className="px-4 py-3 text-gray-600">{departmentMap[item.department_id] ?? '-'}</TableCell>
                                        <TableCell className="px-4 py-3 text-gray-600">{item.year ?? '-'}</TableCell>
                                        <TableCell className="px-4 py-3">
                                            <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${WORKFLOW_STATUS_BADGE_CLASS[item.workflow_status] ?? 'bg-gray-100 text-gray-700'}`}>
                                                {WORKFLOW_STATUS_LABEL[item.workflow_status] ?? item.workflow_status}
                                            </span>
                                        </TableCell>
                                        <TableCell className="px-4 py-3">
                                            <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${ACCESS_LEVEL_BADGE_CLASS[item.access_level] ?? 'bg-gray-100 text-gray-700'}`}>
                                                {ACCESS_LEVEL_LABEL[item.access_level] ?? item.access_level}
                                            </span>
                                        </TableCell>
                                        <TableCell className="px-4 py-3 text-gray-600">
                                            {item.source_core_research_id ? 'Cập nhật bản đã công bố' : 'Công bố lần đầu'}
                                        </TableCell>
                                        <TableCell className="max-w-64 truncate px-4 py-3 text-gray-600" title={item.update_reason ?? undefined}>
                                            {item.update_reason ?? '-'}
                                        </TableCell>
                                        <TableCell className="px-4 py-3 text-gray-600">{item.metadata_quality_score ?? '-'}</TableCell>
                                        <TableCell className="px-4 py-3 text-gray-600">{formatDateTime(item.updated_at ?? item.created_at)}</TableCell>
                                    </TableRow>
                                ))}

                                {!loading && filteredPendingResearches.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={10} className="px-4 py-10 text-center text-sm text-gray-400">
                                            Không có nghiên cứu đang chờ xử lý
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </div>
            ) : (
                <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                    <div className="max-h-[calc(100vh-320px)] overflow-auto">
                        <Table className="min-w-max">
                            <TableHeader className="sticky top-0 z-10 bg-gray-50 text-xs uppercase tracking-wide text-gray-500">
                                <TableRow className="hover:bg-transparent">
                                    <TableHead className="px-4 py-3">Tiêu đề</TableHead>
                                    <TableHead className="px-4 py-3">Loại sản phẩm</TableHead>
                                    <TableHead className="px-4 py-3">Đơn vị</TableHead>
                                    <TableHead className="px-4 py-3">Năm</TableHead>
                                    <TableHead className="px-4 py-3">Mức truy cập</TableHead>
                                    <TableHead className="px-4 py-3">Phiên bản</TableHead>
                                    <TableHead className="px-4 py-3">Ngày công bố</TableHead>
                                    <TableHead className="px-4 py-3 text-right">Thao tác</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {loading && (
                                    <TableRow>
                                        <TableCell colSpan={8} className="px-4 py-6 text-center text-sm text-gray-400">
                                            Đang tải dữ liệu...
                                        </TableCell>
                                    </TableRow>
                                )}

                                {!loading && paginatedPublishedResearches.map((item) => {
                                    const activeRevision = activeRevisionByCore.get(item.research_id)

                                    return (
                                        <TableRow key={item.research_id}>
                                            <TableCell className="max-w-80 truncate px-4 py-3 font-medium text-gray-900" title={item.title}>
                                                {item.title}
                                            </TableCell>
                                            <TableCell className="px-4 py-3 text-gray-600">{outputTypeMap[item.output_type_id] ?? '-'}</TableCell>
                                            <TableCell className="px-4 py-3 text-gray-600">{departmentMap[item.department_id] ?? '-'}</TableCell>
                                            <TableCell className="px-4 py-3 text-gray-600">{item.year ?? '-'}</TableCell>
                                            <TableCell className="px-4 py-3">
                                                <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${ACCESS_LEVEL_BADGE_CLASS[item.access_level] ?? 'bg-gray-100 text-gray-700'}`}>
                                                    {ACCESS_LEVEL_LABEL[item.access_level] ?? item.access_level}
                                                </span>
                                            </TableCell>
                                            <TableCell className="px-4 py-3 font-medium text-gray-700">v{item.version_no}</TableCell>
                                            <TableCell className="px-4 py-3 text-gray-600">{formatDateTime(item.approved_at)}</TableCell>
                                            <TableCell className="px-4 py-3 text-right">
                                                {activeRevision ? (
                                                    <Button
                                                        type="button"
                                                        variant="outline"
                                                        onClick={() => router.push(`/dashboard/data-entry/researches/${activeRevision.staging_id}`)}
                                                    >
                                                        <FilePenLine />
                                                        Mở bản cập nhật
                                                    </Button>
                                                ) : (
                                                    <Button
                                                        type="button"
                                                        variant="outline"
                                                        onClick={() => openRevisionDialog(item)}
                                                    >
                                                        <FilePenLine />
                                                        Kéo về cập nhật
                                                    </Button>
                                                )}
                                            </TableCell>
                                        </TableRow>
                                    )
                                })}

                                {!loading && filteredPublishedResearches.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={8} className="px-4 py-10 text-center text-sm text-gray-400">
                                            Chưa có nghiên cứu đã công bố
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </div>
            )}

            <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm text-gray-500">
                    Trang {currentPage} / {totalPages}
                </p>
                <RtlPagination page={currentPage} totalPages={totalPages} onPageChange={setPage} />
            </div>

            <Dialog
                open={revisionTarget !== null}
                onOpenChange={(open) => {
                    if (!open && !creatingRevision) {
                        setRevisionTarget(null)
                        setUpdateReason('')
                    }
                }}
            >
                <DialogContent className="sm:max-w-md">
                    <DialogHeader>
                        <DialogTitle>Kéo nghiên cứu về cập nhật</DialogTitle>
                        <DialogDescription>
                            Hệ thống sẽ tạo một bản nháp từ phiên bản đang công bố. Bản core chỉ thay đổi và tăng version sau khi bản nháp được duyệt lại.
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-2">
                        <p className="text-sm font-medium text-gray-800">{revisionTarget?.title}</p>
                        <label htmlFor="update-reason" className="text-sm font-medium text-gray-700">
                            Lý do cập nhật <span className="text-red-500">*</span>
                        </label>
                        <Textarea
                            id="update-reason"
                            value={updateReason}
                            onChange={(event) => setUpdateReason(event.target.value)}
                            placeholder="Mô tả nội dung cần thay đổi..."
                            maxLength={1000}
                            rows={4}
                            disabled={creatingRevision}
                        />
                    </div>

                    <DialogFooter>
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => setRevisionTarget(null)}
                            disabled={creatingRevision}
                        >
                            Hủy
                        </Button>
                        <Button
                            type="button"
                            onClick={() => void handleCreateRevision()}
                            disabled={creatingRevision || !updateReason.trim()}
                        >
                            {creatingRevision && <Loader2 className="animate-spin" />}
                            Tạo bản cập nhật
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}
