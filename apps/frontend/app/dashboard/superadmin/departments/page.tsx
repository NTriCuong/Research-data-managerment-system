'use client'

import { useEffect, useMemo, useState } from 'react'
import { MoreHorizontal, Plus } from 'lucide-react'
import { toast } from 'sonner'

import AddDepartmentDialog from '@/components/superadmin/add-department-dialog'
import EditDepartmentDialog from '@/components/superadmin/edit-department-dialog'
import DeleteDepartmentAlert from '@/components/superadmin/delete-department-alert'
import DepartmentDetailDialog from '@/components/superadmin/department-detail-dialog'
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
import {
    referenceService,
    type Department,
} from '@/services/reference/reference.service'

const PAGE_SIZE = 10

export default function SuperAdminDepartmentsPage() {
    const [departments, setDepartments] = useState<Department[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [search, setSearch] = useState('')
    const [statusFilter, setStatusFilter] = useState('')
    const [page, setPage] = useState(1)

    const [openAddDialog, setOpenAddDialog] = useState(false)
    const [editingDept, setEditingDept] = useState<Department | null>(null)
    const [deletingDept, setDeletingDept] = useState<Department | null>(null)
    const [viewingDept, setViewingDept] = useState<Department | null>(null)

    const fetchDepartments = async () => {
        setLoading(true)
        setError('')
        try {
            const data = await referenceService.getDepartments(1, 100)
            setDepartments(data.items)
        } catch (err) {
            setError(parseAxiosError(err).message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchDepartments()
    }, [])

    const departmentMap = useMemo(
        () => Object.fromEntries(departments.map((d) => [d.department_id, d.department_name])),
        [departments]
    )

    const filtered = useMemo(() => {
        const q = search.trim().toLowerCase()
        return departments.filter(
            (d) =>
                (!q ||
                    d.department_name.toLowerCase().includes(q) ||
                    d.department_code.toLowerCase().includes(q) ||
                    d.department_id.toLowerCase().includes(q)) &&
                (!statusFilter ||
                    (statusFilter === 'active' && d.is_active) ||
                    (statusFilter === 'inactive' && !d.is_active))
        )
    }, [departments, search, statusFilter])

    const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
    const currentPage = Math.min(page, totalPages)
    const paginated = useMemo(
        () => filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE),
        [currentPage, filtered]
    )

    const handleToggleStatus = async (dept: Department) => {
        try {
            const updated = await referenceService.updateDepartment(dept.department_id, {
                is_active: !dept.is_active,
            })
            setDepartments((prev) => prev.map((d) => (d.department_id === updated.department_id ? updated : d)))
            toast.success(updated.is_active ? 'Đã kích hoạt đơn vị' : 'Đã vô hiệu hoá đơn vị')
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        }
    }

    const resetFilters = () => {
        setSearch('')
        setStatusFilter('')
        setPage(1)
    }

    return (
        <div className="space-y-6 p-6">
            <div className="flex flex-wrap items-end justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900">Quản lý đơn vị</h1>
                    <p className="mt-1 text-sm text-gray-500">{departments.length} đơn vị</p>
                </div>
            </div>

            <FilterToolbar
                search={search}
                onSearchChange={(value) => {
                    setSearch(value)
                    setPage(1)
                }}
                searchPlaceholder="Tìm theo tên, mã hoặc ID"
                selects={[
                    {
                        key: 'status',
                        label: 'Trạng thái',
                        value: statusFilter,
                        allLabel: 'Tất cả trạng thái',
                        options: [
                            { value: 'active', label: 'Đang hoạt động' },
                            { value: 'inactive', label: 'Không hoạt động' },
                        ],
                        onChange: (value) => {
                            setStatusFilter(value)
                            setPage(1)
                        },
                    },
                ]}
                resultCount={filtered.length}
                onReset={resetFilters}
                rightSlot={
                    <Button onClick={() => setOpenAddDialog(true)}>
                        <Plus size={16} />
                        Đơn vị mới
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
                                <TableHead className="px-4 py-3">Mã đơn vị</TableHead>
                                <TableHead className="px-4 py-3">Tên đơn vị</TableHead>
                                <TableHead className="px-4 py-3">Đơn vị cha</TableHead>
                                <TableHead className="px-4 py-3">Mô tả</TableHead>
                                <TableHead className="px-4 py-3">Trạng thái</TableHead>
                                <TableHead className="px-4 py-3 text-right">Hành động</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading && (
                                <TableRow>
                                    <TableCell colSpan={6} className="px-4 py-6 text-center text-sm text-gray-400">
                                        Đang tải dữ liệu...
                                    </TableCell>
                                </TableRow>
                            )}

                            {!loading && paginated.map((dept) => (
                                <TableRow key={dept.department_id} className="transition hover:bg-blue-50/60">
                                    <TableCell className="px-4 py-3">
                                        <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-700">
                                            {dept.department_code}
                                        </code>
                                    </TableCell>
                                    <TableCell className="px-4 py-3 font-medium text-gray-900">
                                        {dept.department_name}
                                    </TableCell>
                                    <TableCell className="px-4 py-3 text-gray-600">
                                        {dept.parent_department_id
                                            ? departmentMap[dept.parent_department_id] ?? '-'
                                            : <span className="text-gray-400 italic text-sm">Không có</span>
                                        }
                                    </TableCell>
                                    <TableCell className="max-w-64 truncate px-4 py-3 text-gray-600" title={dept.description ?? ''}>
                                        {dept.description || <span className="text-gray-400 italic text-sm">-</span>}
                                    </TableCell>
                                    <TableCell className="px-4 py-3">
                                        <Badge
                                            variant={dept.is_active ? 'default' : 'secondary'}
                                            className={dept.is_active ? 'bg-green-100 text-green-700 hover:bg-green-100' : ''}
                                        >
                                            {dept.is_active ? 'Hoạt động' : 'Không hoạt động'}
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
                                                <DropdownMenuItem onClick={() => setViewingDept(dept)}>
                                                    Xem chi tiết
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onClick={() => setEditingDept(dept)}>
                                                    Sửa thông tin
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onClick={() => handleToggleStatus(dept)}>
                                                    {dept.is_active ? 'Vô hiệu hoá' : 'Kích hoạt'}
                                                </DropdownMenuItem>
                                                <DropdownMenuItem variant="destructive" onClick={() => setDeletingDept(dept)}>
                                                    Xoá
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </TableCell>
                                </TableRow>
                            ))}

                            {!loading && filtered.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={6} className="px-4 py-10 text-center text-sm text-gray-400">
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

            <AddDepartmentDialog
                open={openAddDialog}
                onOpenChange={setOpenAddDialog}
                departments={departments}
                onCreated={(dept) => setDepartments((prev) => [dept, ...prev])}
            />

            <EditDepartmentDialog
                open={!!editingDept}
                onOpenChange={(open) => !open && setEditingDept(null)}
                department={editingDept}
                departments={departments}
                onUpdated={(updated) =>
                    setDepartments((prev) => prev.map((d) => (d.department_id === updated.department_id ? updated : d)))
                }
            />

            <DeleteDepartmentAlert
                open={!!deletingDept}
                onOpenChange={(open) => !open && setDeletingDept(null)}
                department={deletingDept}
                onDeleted={(id) => setDepartments((prev) => prev.filter((d) => d.department_id !== id))}
            />

            <DepartmentDetailDialog
                open={!!viewingDept}
                onOpenChange={(open) => !open && setViewingDept(null)}
                department={viewingDept}
                departmentMap={departmentMap}
            />
        </div>
    )
}
