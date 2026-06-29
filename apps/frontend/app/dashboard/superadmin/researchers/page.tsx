'use client'

import { useEffect, useMemo, useState } from 'react'
import { MoreHorizontal, Plus } from 'lucide-react'

import AddResearcherDialog from '@/components/superadmin/add-researcher-dialog'
import EditResearcherDialog from '@/components/superadmin/edit-researcher-dialog'
import DeleteResearcherAlert from '@/components/superadmin/delete-researcher-alert'
import ResearcherDetailDialog from '@/components/superadmin/researcher-detail-dialog'
import FilterToolbar from '@/components/dashboard/filter-toolbar'
import { Button } from '@/components/ui/button'
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
import { Badge } from '@/components/ui/badge'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { referenceService, type Department, type Researcher } from '@/services/reference/reference.service'

const PAGE_SIZE = 10

export default function SuperAdminResearchersPage() {
    const [researchers, setResearchers] = useState<Researcher[]>([])
    const [departments, setDepartments] = useState<Department[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [search, setSearch] = useState('')
    const [typeFilter, setTypeFilter] = useState('')
    const [departmentFilter, setDepartmentFilter] = useState('')
    const [page, setPage] = useState(1)

    const [openAddDialog, setOpenAddDialog] = useState(false)
    const [editingItem, setEditingItem] = useState<Researcher | null>(null)
    const [deletingItem, setDeletingItem] = useState<Researcher | null>(null)
    const [viewingItem, setViewingItem] = useState<Researcher | null>(null)

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true)
            setError('')
            try {
                const [resRes, deptRes] = await Promise.all([
                    referenceService.getResearchers(1, 100),
                    referenceService.getDepartments(1, 100).catch(() => null),
                ])
                setResearchers(resRes.items)
                if (deptRes) setDepartments(deptRes.items)
            } catch (err) {
                setError(parseAxiosError(err).message)
            } finally {
                setLoading(false)
            }
        }
        fetchData()
    }, [])

    const departmentMap = useMemo(
        () => Object.fromEntries(departments.map((d) => [d.department_id, d.department_name])),
        [departments]
    )

    const filtered = useMemo(() => {
        const q = search.trim().toLowerCase()
        return researchers.filter(
            (r) =>
                (!q ||
                    r.full_name.toLowerCase().includes(q) ||
                    (r.email ?? '').toLowerCase().includes(q) ||
                    (r.researcher_code ?? '').toLowerCase().includes(q) ||
                    r.researcher_id.toLowerCase().includes(q)) &&
                (!typeFilter ||
                    (typeFilter === 'internal' && r.is_internal) ||
                    (typeFilter === 'external' && !r.is_internal)) &&
                (!departmentFilter || r.department_id === departmentFilter)
        )
    }, [researchers, search, typeFilter, departmentFilter])

    const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
    const currentPage = Math.min(page, totalPages)
    const paginated = useMemo(
        () => filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE),
        [currentPage, filtered]
    )

    const resetFilters = () => {
        setSearch('')
        setTypeFilter('')
        setDepartmentFilter('')
        setPage(1)
    }

    return (
        <div className="space-y-6 p-6">
            <div className="flex flex-wrap items-end justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900">Quản lý nhà nghiên cứu</h1>
                    <p className="mt-1 text-sm text-gray-500">{researchers.length} nhà nghiên cứu</p>
                </div>
            </div>

            <FilterToolbar
                search={search}
                onSearchChange={(value) => {
                    setSearch(value)
                    setPage(1)
                }}
                searchPlaceholder="Tìm theo tên, email, mã hoặc ID"
                selects={[
                    {
                        key: 'type',
                        label: 'Loại',
                        value: typeFilter,
                        allLabel: 'Tất cả loại',
                        options: [
                            { value: 'internal', label: 'Nội bộ' },
                            { value: 'external', label: 'Bên ngoài' },
                        ],
                        onChange: (value) => {
                            setTypeFilter(value)
                            setPage(1)
                        },
                    },
                    {
                        key: 'department',
                        label: 'Đơn vị',
                        value: departmentFilter,
                        allLabel: 'Tất cả đơn vị',
                        options: departments.map((d) => ({ value: d.department_id, label: d.department_name })),
                        onChange: (value) => {
                            setDepartmentFilter(value)
                            setPage(1)
                        },
                    },
                ]}
                resultCount={filtered.length}
                onReset={resetFilters}
                rightSlot={
                    <Button onClick={() => setOpenAddDialog(true)}>
                        <Plus size={16} />
                        Nhà nghiên cứu mới
                    </Button>
                }
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
                                <TableHead className="px-4 py-3">Họ tên</TableHead>
                                <TableHead className="px-4 py-3">Email</TableHead>
                                <TableHead className="px-4 py-3">Học hàm</TableHead>
                                <TableHead className="px-4 py-3">Mã NNC</TableHead>
                                <TableHead className="px-4 py-3">Đơn vị</TableHead>
                                <TableHead className="px-4 py-3">Loại</TableHead>
                                <TableHead className="px-4 py-3 text-right">Hành động</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading && (
                                <TableRow>
                                    <TableCell colSpan={7} className="px-4 py-6 text-center text-sm text-gray-400">
                                        Đang tải dữ liệu...
                                    </TableCell>
                                </TableRow>
                            )}

                            {!loading && paginated.map((r) => (
                                <TableRow key={r.researcher_id} className="transition hover:bg-blue-50/60">
                                    <TableCell className="px-4 py-3 font-medium text-gray-900">
                                        {r.full_name}
                                    </TableCell>
                                    <TableCell className="px-4 py-3 text-gray-600">
                                        {r.email || <span className="text-gray-400 italic text-sm">-</span>}
                                    </TableCell>
                                    <TableCell className="px-4 py-3 text-gray-600">
                                        {r.academic_title || <span className="text-gray-400 italic text-sm">-</span>}
                                    </TableCell>
                                    <TableCell className="px-4 py-3">
                                        {r.researcher_code
                                            ? <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-700">{r.researcher_code}</code>
                                            : <span className="text-gray-400 italic text-sm">-</span>
                                        }
                                    </TableCell>
                                    <TableCell className="px-4 py-3 text-gray-600">
                                        {r.department_id
                                            ? departmentMap[r.department_id] ?? '-'
                                            : <span className="text-gray-400 italic text-sm">-</span>
                                        }
                                    </TableCell>
                                    <TableCell className="px-4 py-3">
                                        <Badge
                                            variant={r.is_internal ? 'default' : 'secondary'}
                                            className={r.is_internal ? 'bg-blue-100 text-blue-700 hover:bg-blue-100' : ''}
                                        >
                                            {r.is_internal ? 'Nội bộ' : 'Bên ngoài'}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="px-4 py-3 text-right">
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Button variant="ghost" size="icon" aria-label="Mở menu hành động">
                                                    <MoreHorizontal size={16} />
                                                </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                                <DropdownMenuItem onClick={() => setViewingItem(r)}>
                                                    Xem chi tiết
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onClick={() => setEditingItem(r)}>
                                                    Sửa thông tin
                                                </DropdownMenuItem>
                                                <DropdownMenuItem variant="destructive" onClick={() => setDeletingItem(r)}>
                                                    Xoá
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </TableCell>
                                </TableRow>
                            ))}

                            {!loading && filtered.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={7} className="px-4 py-10 text-center text-sm text-gray-400">
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

            <AddResearcherDialog
                open={openAddDialog}
                onOpenChange={setOpenAddDialog}
                departments={departments}
                onCreated={(item) => setResearchers((prev) => [item, ...prev])}
            />

            <EditResearcherDialog
                open={!!editingItem}
                onOpenChange={(open) => !open && setEditingItem(null)}
                researcher={editingItem}
                departments={departments}
                onUpdated={(updated) =>
                    setResearchers((prev) => prev.map((r) => (r.researcher_id === updated.researcher_id ? updated : r)))
                }
            />

            <DeleteResearcherAlert
                open={!!deletingItem}
                onOpenChange={(open) => !open && setDeletingItem(null)}
                researcher={deletingItem}
                onDeleted={(id) => setResearchers((prev) => prev.filter((r) => r.researcher_id !== id))}
            />

            <ResearcherDetailDialog
                open={!!viewingItem}
                onOpenChange={(open) => !open && setViewingItem(null)}
                researcher={viewingItem}
                departmentMap={departmentMap}
            />
        </div>
    )
}
