'use client'

import { useEffect, useMemo, useState } from 'react'
import { MoreHorizontal, Plus } from 'lucide-react'
import { toast } from 'sonner'

import AddOutputTypeDialog from '@/components/superadmin/add-output-type-dialog'
import EditOutputTypeDialog from '@/components/superadmin/edit-output-type-dialog'
import DeleteOutputTypeAlert from '@/components/superadmin/delete-output-type-alert'
import OutputTypeDetailDialog from '@/components/superadmin/output-type-detail-dialog'
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
import { referenceService, type OutputType } from '@/services/reference/reference.service'

const PAGE_SIZE = 10

export default function SuperAdminOutputTypePage() {
    const [items, setItems] = useState<OutputType[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [search, setSearch] = useState('')
    const [statusFilter, setStatusFilter] = useState('')
    const [page, setPage] = useState(1)

    const [openAddDialog, setOpenAddDialog] = useState(false)
    const [editingItem, setEditingItem] = useState<OutputType | null>(null)
    const [deletingItem, setDeletingItem] = useState<OutputType | null>(null)
    const [viewingItem, setViewingItem] = useState<OutputType | null>(null)

    useEffect(() => {
        const fetch = async () => {
            setLoading(true)
            setError('')
            try {
                const data = await referenceService.getOutputTypes(1, 100)
                setItems(data.items)
            } catch (err) {
                setError(parseAxiosError(err).message)
            } finally {
                setLoading(false)
            }
        }
        fetch()
    }, [])

    const filtered = useMemo(() => {
        const q = search.trim().toLowerCase()
        return items.filter(
            (item) =>
                (!q ||
                    item.type_name.toLowerCase().includes(q) ||
                    item.type_code.toLowerCase().includes(q) ||
                    item.output_type_id.toLowerCase().includes(q)) &&
                (!statusFilter ||
                    (statusFilter === 'active' && item.is_active) ||
                    (statusFilter === 'inactive' && !item.is_active))
        )
    }, [items, search, statusFilter])

    const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
    const currentPage = Math.min(page, totalPages)
    const paginated = useMemo(
        () => filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE),
        [currentPage, filtered]
    )

    const handleToggleStatus = async (item: OutputType) => {
        try {
            const updated = await referenceService.updateOutputType(item.output_type_id, {
                is_active: !item.is_active,
            })
            setItems((prev) => prev.map((o) => (o.output_type_id === updated.output_type_id ? updated : o)))
            toast.success(updated.is_active ? 'Đã kích hoạt loại sản phẩm' : 'Đã vô hiệu hoá loại sản phẩm')
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
                    <h1 className="text-2xl font-semibold text-gray-900">Quản lý loại sản phẩm</h1>
                    <p className="mt-1 text-sm text-gray-500">{items.length} loại sản phẩm</p>
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
                        Loại sản phẩm mới
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
                                <TableHead className="px-4 py-3">Mã loại</TableHead>
                                <TableHead className="px-4 py-3">Tên loại sản phẩm</TableHead>
                                <TableHead className="px-4 py-3">Mô tả</TableHead>
                                <TableHead className="px-4 py-3">Trạng thái</TableHead>
                                <TableHead className="px-4 py-3 text-right">Hành động</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading && (
                                <TableRow>
                                    <TableCell colSpan={5} className="px-4 py-6 text-center text-sm text-gray-400">
                                        Đang tải dữ liệu...
                                    </TableCell>
                                </TableRow>
                            )}

                            {!loading && paginated.map((item) => (
                                <TableRow key={item.output_type_id} className="transition hover:bg-blue-50/60">
                                    <TableCell className="px-4 py-3">
                                        <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-700">
                                            {item.type_code}
                                        </code>
                                    </TableCell>
                                    <TableCell className="px-4 py-3 font-medium text-gray-900">
                                        {item.type_name}
                                    </TableCell>
                                    <TableCell className="max-w-64 truncate px-4 py-3 text-gray-600" title={item.description ?? ''}>
                                        {item.description || <span className="text-gray-400 italic text-sm">-</span>}
                                    </TableCell>
                                    <TableCell className="px-4 py-3">
                                        <Badge
                                            variant={item.is_active ? 'default' : 'secondary'}
                                            className={item.is_active ? 'bg-green-100 text-green-700 hover:bg-green-100' : ''}
                                        >
                                            {item.is_active ? 'Hoạt động' : 'Không hoạt động'}
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
                                                <DropdownMenuItem onClick={() => setViewingItem(item)}>
                                                    Xem chi tiết
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onClick={() => setEditingItem(item)}>
                                                    Sửa thông tin
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onClick={() => handleToggleStatus(item)}>
                                                    {item.is_active ? 'Vô hiệu hoá' : 'Kích hoạt'}
                                                </DropdownMenuItem>
                                                <DropdownMenuItem variant="destructive" onClick={() => setDeletingItem(item)}>
                                                    Xoá
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </TableCell>
                                </TableRow>
                            ))}

                            {!loading && filtered.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={5} className="px-4 py-10 text-center text-sm text-gray-400">
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

            <AddOutputTypeDialog
                open={openAddDialog}
                onOpenChange={setOpenAddDialog}
                onCreated={(item) => setItems((prev) => [item, ...prev])}
            />

            <EditOutputTypeDialog
                open={!!editingItem}
                onOpenChange={(open) => !open && setEditingItem(null)}
                outputType={editingItem}
                onUpdated={(updated) =>
                    setItems((prev) => prev.map((o) => (o.output_type_id === updated.output_type_id ? updated : o)))
                }
            />

            <DeleteOutputTypeAlert
                open={!!deletingItem}
                onOpenChange={(open) => !open && setDeletingItem(null)}
                outputType={deletingItem}
                onDeleted={(id) => setItems((prev) => prev.filter((o) => o.output_type_id !== id))}
            />

            <OutputTypeDetailDialog
                open={!!viewingItem}
                onOpenChange={(open) => !open && setViewingItem(null)}
                outputType={viewingItem}
            />
        </div>
    )
}
