'use client'

import { useEffect, useMemo, useState } from 'react'
import { Search } from 'lucide-react'
import { useRouter } from 'next/navigation'

import FilterToolbar, { type FilterSelect } from '@/components/dashboard/filter-toolbar'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { parseAxiosError } from '@/lib/axios/error-paser'
import {
    ACCESS_LEVEL_BADGE_CLASS,
    ACCESS_LEVEL_LABEL,
    WORKFLOW_STATUS_BADGE_CLASS,
    WORKFLOW_STATUS_LABEL,
} from '@/lib/constants/workflow'
import { referenceService } from '@/services/reference/reference.service'
import { reviewerService } from '@/services/reviewer/reviewer.service'
import { type StagingResearchObject } from '@/services/data-entry/data-entry.service'

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
    const [departmentFilter, setDepartmentFilter] = useState('')
    const [outputTypeFilter, setOutputTypeFilter] = useState('')
    const [accessFilter, setAccessFilter] = useState('')
    const [yearFilter, setYearFilter] = useState('')

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
        return dataResearch.filter((item) => {
            const matchesSearch =
                !q ||
                item.title.toLowerCase().includes(q) ||
                item.staging_id.toLowerCase().includes(q)
            const matchesDepartment = !departmentFilter || item.department_id === departmentFilter
            const matchesOutputType = !outputTypeFilter || item.output_type_id === outputTypeFilter
            const matchesAccess = !accessFilter || item.access_level === accessFilter
            const matchesYear = !yearFilter || String(item.year ?? '') === yearFilter

            return matchesSearch && matchesDepartment && matchesOutputType && matchesAccess && matchesYear
        })
    }, [accessFilter, dataResearch, departmentFilter, outputTypeFilter, search, yearFilter])

    const yearOptions = useMemo(
        () =>
            Array.from(new Set(dataResearch.map((item) => item.year).filter((year): year is number => year !== null)))
                .sort((a, b) => b - a)
                .map((year) => ({ value: String(year), label: String(year) })),
        [dataResearch]
    )

    const filterSelects: FilterSelect[] = [
        {
            key: 'output-type',
            label: 'Loại sản phẩm',
            value: outputTypeFilter,
            allLabel: 'Tất cả loại',
            options: Object.entries(outputTypeMap).map(([value, label]) => ({ value, label })),
            onChange: setOutputTypeFilter,
        },
        {
            key: 'department',
            label: 'Đơn vị',
            value: departmentFilter,
            allLabel: 'Tất cả đơn vị',
            options: Object.entries(departmentMap).map(([value, label]) => ({ value, label })),
            onChange: setDepartmentFilter,
        },
        {
            key: 'access',
            label: 'Mức truy cập',
            value: accessFilter,
            allLabel: 'Tất cả mức',
            options: Object.entries(ACCESS_LEVEL_LABEL).map(([value, label]) => ({ value, label })),
            onChange: setAccessFilter,
        },
        {
            key: 'year',
            label: 'Năm',
            value: yearFilter,
            allLabel: 'Tất cả năm',
            options: yearOptions,
            onChange: setYearFilter,
        },
    ]

    const resetFilters = () => {
        setSearch('')
        setDepartmentFilter('')
        setOutputTypeFilter('')
        setAccessFilter('')
        setYearFilter('')
    }

    return (
        <div className="space-y-6 p-6">
            <div className="flex flex-wrap items-end justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900">Nghiên cứu chờ kiểm duyệt</h1>
                    <p className="mt-1 text-sm text-gray-500">
                        {dataResearch.length} bản ghi đang chờ kiểm duyệt
                    </p>
                </div>

                <div className="hidden">
                    <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Tìm theo tiêu đề..."
                        className="w-64 rounded-lg border border-gray-200 py-2 pl-9 pr-3 text-sm focus:border-blue-400 focus:outline-none"
                    />
                </div>
            </div>

            <FilterToolbar
                search={search}
                onSearchChange={setSearch}
                searchPlaceholder="Tìm kiếm ..."
                selects={filterSelects}
                resultCount={filteredData.length}
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
                                <TableHead className="px-4 py-3">Tiêu đề</TableHead>
                                <TableHead className="px-4 py-3">Loại sản phẩm</TableHead>
                                <TableHead className="px-4 py-3">Đơn vị</TableHead>
                                <TableHead className="px-4 py-3">Năm</TableHead>
                                <TableHead className="px-4 py-3">Trạng thái</TableHead>
                                <TableHead className="px-4 py-3">Mức truy cập</TableHead>
                                <TableHead className="px-4 py-3">Điểm chất lượng</TableHead>
                                <TableHead className="px-4 py-3">Ngày gửi</TableHead>
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

                            {!loading && filteredData.map((item) => (
                                <TableRow
                                    key={item.staging_id}
                                    onClick={() => router.push(`/dashboard/review/researches/${item.staging_id}`)}
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
                                    <TableCell className="px-4 py-3 text-gray-600">{item.metadata_quality_score ?? '-'}</TableCell>
                                    <TableCell className="px-4 py-3 text-gray-600">{formatDateTime(item.submitted_at)}</TableCell>
                                </TableRow>
                            ))}

                            {!loading && filteredData.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={8} className="px-4 py-10 text-center text-sm text-gray-400">
                                        Không có dữ liệu
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </div>
            </div>
        </div>
    )
}
