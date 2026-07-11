'use client'

import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { ExternalLink, Eye, FileText, MoreHorizontal } from 'lucide-react'

import FilterToolbar, { type FilterSelect } from '@/components/dashboard/filter-toolbar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { RtlPagination } from '@/components/ui/rtl-pagination'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { ACCESS_LEVEL_BADGE_CLASS, ACCESS_LEVEL_LABEL } from '@/lib/constants/workflow'
import {
    coreRepositoryService,
    type CoreResearchObject,
    type CoreResearchObjectDetail,
} from '@/services/core/core-repository.service'
import { referenceService, type Department, type OutputType } from '@/services/reference/reference.service'

const PAGE_SIZE = 10

function formatDateTime(value: string | null) {
    if (!value) return '-'
    return new Date(value).toLocaleString('vi-VN')
}

function formatDate(value: string | null) {
    if (!value) return '-'
    return new Date(value).toLocaleDateString('vi-VN')
}

function shortId(value: string) {
    return value.slice(0, 8)
}

export default function SuperAdminResearchesPage() {
    const [researches, setResearches] = useState<CoreResearchObject[]>([])
    const [departments, setDepartments] = useState<Department[]>([])
    const [outputTypes, setOutputTypes] = useState<OutputType[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [search, setSearch] = useState('')
    const [departmentFilter, setDepartmentFilter] = useState('')
    const [outputTypeFilter, setOutputTypeFilter] = useState('')
    const [accessFilter, setAccessFilter] = useState('')
    const [yearFilter, setYearFilter] = useState('')
    const [page, setPage] = useState(1)

    const [viewingId, setViewingId] = useState<string | null>(null)
    const [detail, setDetail] = useState<CoreResearchObjectDetail | null>(null)
    const [detailLoading, setDetailLoading] = useState(false)
    const [detailError, setDetailError] = useState('')

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true)
            setError('')
            try {
                const [records, departmentRes, outputTypeRes] = await Promise.all([
                    coreRepositoryService.listCoreRecords(100, 0),
                    referenceService.getDepartments(1, 100).catch(() => null),
                    referenceService.getOutputTypes(1, 100).catch(() => null),
                ])
                setResearches(records)
                if (departmentRes) setDepartments(departmentRes.items)
                if (outputTypeRes) setOutputTypes(outputTypeRes.items)
            } catch (err) {
                setError(parseAxiosError(err).message)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [])

    useEffect(() => {
        if (!viewingId) return

        coreRepositoryService
            .getCoreRecord(viewingId)
            .then(setDetail)
            .catch((err) => setDetailError(parseAxiosError(err).message))
            .finally(() => setDetailLoading(false))
    }, [viewingId])

    const openDetail = (researchId: string) => {
        setDetail(null)
        setDetailError('')
        setDetailLoading(true)
        setViewingId(researchId)
    }

    const departmentMap = useMemo(
        () => Object.fromEntries(departments.map((department) => [department.department_id, department.department_name])),
        [departments]
    )

    const outputTypeMap = useMemo(
        () => Object.fromEntries(outputTypes.map((type) => [type.output_type_id, type.type_name])),
        [outputTypes]
    )

    const filtered = useMemo(() => {
        const q = search.trim().toLowerCase()
        return researches.filter((item) => {
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
    }, [accessFilter, departmentFilter, outputTypeFilter, researches, search, yearFilter])

    const yearOptions = useMemo(
        () =>
            Array.from(new Set(researches.map((item) => item.year).filter((year): year is number => year !== null)))
                .sort((a, b) => b - a)
                .map((year) => ({ value: String(year), label: String(year) })),
        [researches]
    )

    const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
    const currentPage = Math.min(page, totalPages)
    const paginated = useMemo(
        () => filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE),
        [currentPage, filtered]
    )

    const filterSelects: FilterSelect[] = [
        {
            key: 'output-type',
            label: 'Loại sản phẩm',
            value: outputTypeFilter,
            allLabel: 'Tất cả loại',
            options: outputTypes.map((type) => ({ value: type.output_type_id, label: type.type_name })),
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
            options: departments.map((department) => ({ value: department.department_id, label: department.department_name })),
            onChange: (value) => {
                setDepartmentFilter(value)
                setPage(1)
            },
        },
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
        setAccessFilter('')
        setYearFilter('')
        setPage(1)
    }

    return (
        <div className="space-y-6 p-6">
            <div className="flex flex-wrap items-end justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900">Kho nghiên cứu</h1>
                    <p className="mt-1 text-sm text-gray-500">{researches.length} bản ghi đã được duyệt</p>
                </div>
            </div>

            <FilterToolbar
                search={search}
                onSearchChange={(value) => {
                    setSearch(value)
                    setPage(1)
                }}
                searchPlaceholder="Tìm theo tiêu đề hoặc ID nghiên cứu"
                selects={filterSelects}
                resultCount={filtered.length}
                onReset={resetFilters}
            />

            {error && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-500">
                    {error}
                </p>
            )}

            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                <div className="max-h-[calc(100vh-260px)] overflow-auto">
                    <Table className="min-w-max">
                        <TableHeader className="sticky top-0 z-10 bg-gray-50 text-xs uppercase tracking-wide text-gray-500">
                            <TableRow className="hover:bg-transparent">
                                <TableHead className="px-4 py-3">ID</TableHead>
                                <TableHead className="px-4 py-3">Tiêu đề</TableHead>
                                <TableHead className="px-4 py-3">Loại sản phẩm</TableHead>
                                <TableHead className="px-4 py-3">Đơn vị</TableHead>
                                <TableHead className="px-4 py-3">Năm</TableHead>
                                <TableHead className="px-4 py-3">Mức truy cập</TableHead>
                                <TableHead className="px-4 py-3">Phiên bản</TableHead>
                                <TableHead className="px-4 py-3">Điểm chất lượng</TableHead>
                                <TableHead className="px-4 py-3">Ngày duyệt</TableHead>
                                <TableHead className="px-4 py-3 text-right">Hành động</TableHead>
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

                            {!loading && paginated.map((item) => (
                                <TableRow key={item.research_id} className="transition hover:bg-blue-50/60">
                                    <TableCell className="px-4 py-3">
                                        <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-700" title={item.research_id}>
                                            {shortId(item.research_id)}
                                        </code>
                                    </TableCell>
                                    <TableCell className="max-w-96 truncate px-4 py-3 font-medium text-gray-900" title={item.title}>
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
                                    <TableCell className="px-4 py-3">
                                        <Badge variant={item.is_current ? 'default' : 'secondary'} className={item.is_current ? 'bg-green-100 text-green-700 hover:bg-green-100' : ''}>
                                            v{item.version_no}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="px-4 py-3 text-gray-600">{item.metadata_quality_score ?? '-'}</TableCell>
                                    <TableCell className="px-4 py-3 text-gray-600">{formatDateTime(item.approved_at)}</TableCell>
                                    <TableCell className="px-4 py-3 text-right">
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Button variant="ghost" size="icon" aria-label="Mở menu hành động">
                                                    <MoreHorizontal size={16} />
                                                </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                                <DropdownMenuItem onClick={() => openDetail(item.research_id)}>
                                                    <Eye size={16} />
                                                    Xem chi tiết
                                                </DropdownMenuItem>
                                                <DropdownMenuItem asChild>
                                                    <Link href={`/researches/${item.research_id}`} target="_blank">
                                                        <ExternalLink size={16} />
                                                        Mở trang công khai
                                                    </Link>
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </TableCell>
                                </TableRow>
                            ))}

                            {!loading && filtered.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={10} className="px-4 py-10 text-center text-sm text-gray-400">
                                        Không có dữ liệu
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm text-gray-500">
                    Trang {currentPage} / {totalPages}
                </p>
                <RtlPagination page={currentPage} totalPages={totalPages} onPageChange={setPage} />
            </div>

            <ResearchDetailDialog
                open={!!viewingId}
                onOpenChange={(open) => {
                    if (!open) {
                        setViewingId(null)
                        setDetail(null)
                        setDetailError('')
                        setDetailLoading(false)
                    }
                }}
                detail={detail}
                loading={detailLoading}
                error={detailError}
                departmentMap={departmentMap}
                outputTypeMap={outputTypeMap}
            />
        </div>
    )
}

function ResearchDetailDialog({
    open,
    onOpenChange,
    detail,
    loading,
    error,
    departmentMap,
    outputTypeMap,
}: {
    open: boolean
    onOpenChange: (open: boolean) => void
    detail: CoreResearchObjectDetail | null
    loading: boolean
    error: string
    departmentMap: Record<string, string>
    outputTypeMap: Record<string, string>
}) {
    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-3xl">
                <DialogHeader>
                    <DialogTitle>Chi tiết nghiên cứu</DialogTitle>
                    <DialogDescription>
                        Thông tin bản ghi đã được duyệt vào kho nghiên cứu.
                    </DialogDescription>
                </DialogHeader>

                {loading && <p className="py-8 text-center text-sm text-gray-400">Đang tải chi tiết...</p>}

                {!loading && error && (
                    <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-500">
                        {error}
                    </p>
                )}

                {!loading && detail && (
                    <div className="space-y-5">
                        <div>
                            <div className="flex flex-wrap items-center gap-2">
                                <Badge variant="secondary">{outputTypeMap[detail.output_type_id] ?? 'Chưa phân loại'}</Badge>
                                {detail.year ? <Badge variant="outline">{detail.year}</Badge> : null}
                                <Badge variant="outline">v{detail.version_no}</Badge>
                            </div>
                            <h2 className="mt-3 text-xl font-semibold leading-8 text-gray-900">{detail.title}</h2>
                            <p className="mt-2 text-sm text-gray-500">
                                ID: <code className="rounded bg-gray-100 px-1 py-0.5">{detail.research_id}</code>
                            </p>
                        </div>

                        <div className="grid gap-3 text-sm sm:grid-cols-2">
                            <Meta label="Đơn vị" value={departmentMap[detail.department_id] ?? '-'} />
                            <Meta label="Mức truy cập" value={ACCESS_LEVEL_LABEL[detail.access_level] ?? detail.access_level} />
                            <Meta label="Ngày duyệt" value={formatDateTime(detail.approved_at)} />
                            <Meta label="Ngày phát hành" value={formatDate(detail.date_issued)} />
                            <Meta label="Nhà xuất bản" value={detail.publisher || '-'} />
                            <Meta label="Ngôn ngữ" value={detail.language || '-'} />
                            <Meta label="Mã định danh" value={detail.identifier || '-'} />
                            <Meta label="Điểm chất lượng" value={String(detail.metadata_quality_score ?? '-')} />
                        </div>

                        <Section title="Mô tả" value={detail.description} />
                        <Section title="Tóm tắt" value={detail.abstract} />

                        <div>
                            <h3 className="mb-2 text-sm font-semibold text-gray-900">Tác giả</h3>
                            {detail.authors.length === 0 ? (
                                <p className="text-sm text-gray-400">Chưa có tác giả.</p>
                            ) : (
                                <div className="grid gap-2">
                                    {detail.authors.map((author) => (
                                        <div key={author.core_author_id} className="rounded-lg border border-gray-200 p-3">
                                            <p className="font-medium text-gray-900">
                                                {author.author_order}. {author.full_name}
                                            </p>
                                            <p className="mt-1 text-sm text-gray-500">
                                                {author.affiliation || '-'} · {author.author_role}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div>
                            <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-gray-900">
                                <FileText size={16} />
                                Tài liệu đính kèm
                            </h3>
                            {detail.file_attachments.length === 0 ? (
                                <p className="text-sm text-gray-400">Chưa có file đính kèm.</p>
                            ) : (
                                <div className="grid gap-2">
                                    {detail.file_attachments.map((file) => (
                                        <div key={file.file_id} className="flex items-center justify-between gap-3 rounded-lg border border-gray-200 p-3">
                                            <div className="min-w-0">
                                                <p className="truncate font-medium text-gray-900">{file.original_filename}</p>
                                                <p className="text-xs text-gray-500">{file.mime_type} · {formatDateTime(file.uploaded_at)}</p>
                                            </div>
                                            <Badge variant="outline">{ACCESS_LEVEL_LABEL[file.access_level] ?? file.access_level}</Badge>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                <DialogFooter>
                    {detail && (
                        <Button asChild variant="outline">
                            <Link href={`/researches/${detail.research_id}`} target="_blank">
                                <ExternalLink size={16} />
                                Mở trang công khai
                            </Link>
                        </Button>
                    )}
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}

function Meta({ label, value }: { label: string; value: string }) {
    return (
        <div>
            <p className="text-xs font-medium uppercase text-gray-500">{label}</p>
            <p className="mt-1 text-gray-900">{value}</p>
        </div>
    )
}

function Section({ title, value }: { title: string; value: string | null }) {
    return (
        <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-900">{title}</h3>
            <p className="rounded-lg border border-gray-200 bg-gray-50 p-3 text-sm leading-6 text-gray-600">
                {value || 'Chưa cập nhật.'}
            </p>
        </div>
    )
}
