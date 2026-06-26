'use client'

import { useEffect, useMemo, useState } from 'react'
import { MoreHorizontal, Plus, Search } from 'lucide-react'
import { toast } from 'sonner'

import FilterToolbar, { type FilterSelect } from '@/components/dashboard/filter-toolbar'
import DeleteUserAlert from '@/components/superadmin/delete-user-alert'
import AddUserDialog from '@/components/superadmin/add-user-dialog'
import EditUserDialog from '@/components/superadmin/edit-user-dialog'
import { Button } from '@/components/ui/button'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
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
    referenceService,
    type AppUser,
    type Department,
    type Role,
} from '@/services/reference/reference.service'

function formatDateTime(value: string | null) {
    if (!value) return '-'
    return new Date(value).toLocaleString('vi-VN')
}

export default function SuperAdminUsersPage() {
    const [users, setUsers] = useState<AppUser[]>([])
    const [roles, setRoles] = useState<Role[]>([])
    const [departments, setDepartments] = useState<Department[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [search, setSearch] = useState('')
    const [roleFilter, setRoleFilter] = useState('')
    const [departmentFilter, setDepartmentFilter] = useState('')
    const [statusFilter, setStatusFilter] = useState('')

    const [openAddDialog, setOpenAddDialog] = useState(false)
    const [editingUser, setEditingUser] = useState<AppUser | null>(null)
    const [deletingUser, setDeletingUser] = useState<AppUser | null>(null)

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true)
            setError('')
            try {
                const data = await referenceService.getUsers({ limit: 100 })
                setUsers(data)
            } catch (err) {
                setError(parseAxiosError(err).message)
            }

            const [rolesRes, departmentsRes] = await Promise.all([
                referenceService.getRoles().catch(() => []),
                referenceService.getDepartments().catch(() => null),
            ])
            setRoles(rolesRes)
            if (departmentsRes) setDepartments(departmentsRes.items)

            setLoading(false)
        }

        fetchData()
    }, [])

    const roleMap = useMemo(() => Object.fromEntries(roles.map((r) => [r.role_id, r.role_name])), [roles])
    const departmentMap = useMemo(() => Object.fromEntries(departments.map((d) => [d.department_id, d.department_name])), [departments])

    const filteredUsers = useMemo(() => {
        const q = search.trim().toLowerCase()
        return users.filter(
            (u) =>
                (!q ||
                    u.full_name.toLowerCase().includes(q) ||
                    u.username.toLowerCase().includes(q) ||
                    u.email.toLowerCase().includes(q) ||
                    u.user_id.toLowerCase().includes(q)) &&
                (!roleFilter || u.role_id === roleFilter) &&
                (!departmentFilter || u.department_id === departmentFilter) &&
                (!statusFilter || u.status === statusFilter)
        )
    }, [departmentFilter, roleFilter, search, statusFilter, users])

    const filterSelects: FilterSelect[] = [
        {
            key: 'role',
            label: 'Vai trò',
            value: roleFilter,
            allLabel: 'Tất cả vai trò',
            options: roles.map((role) => ({ value: role.role_id, label: role.role_name })),
            onChange: setRoleFilter,
        },
        {
            key: 'department',
            label: 'Đơn vị',
            value: departmentFilter,
            allLabel: 'Tất cả đơn vị',
            options: departments.map((department) => ({ value: department.department_id, label: department.department_name })),
            onChange: setDepartmentFilter,
        },
        {
            key: 'status',
            label: 'Trạng thái',
            value: statusFilter,
            allLabel: 'Tất cả trạng thái',
            options: [
                { value: 'active', label: 'Đang hoạt động' },
                { value: 'disabled', label: 'Đã khóa' },
            ],
            onChange: setStatusFilter,
        },
    ]

    const resetFilters = () => {
        setSearch('')
        setRoleFilter('')
        setDepartmentFilter('')
        setStatusFilter('')
    }

    const handleToggleStatus = async (user: AppUser) => {
        const nextStatus = user.status === 'active' ? 'disabled' : 'active'
        try {
            const updated = await referenceService.updateUserStatus(user.user_id, nextStatus)
            setUsers((prev) => prev.map((u) => (u.user_id === updated.user_id ? updated : u)))
            toast.success(nextStatus === 'active' ? 'Đã kích hoạt người dùng' : 'Đã vô hiệu hoá người dùng')
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        }
    }

    return (
        <div className="space-y-6 p-6">
            <div className="flex flex-wrap items-end justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900">Quản lý người dùng</h1>
                    <p className="mt-1 text-sm text-gray-500">{users.length} người dùng</p>
                </div>

                <div className="hidden">
                    <div className="relative">
                        <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                        <Input
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="Tìm theo tên, username, email..."
                            autoComplete="off"
                            className="w-64 pl-9"
                        />
                    </div>

                    <Button onClick={() => setOpenAddDialog(true)}>
                        <Plus size={16} />
                        Thêm người dùng
                    </Button>
                </div>
            </div>

            <FilterToolbar
                search={search}
                onSearchChange={setSearch}
                searchPlaceholder="Tìm theo tên, username, email hoặc ID"
                selects={filterSelects}
                resultCount={filteredUsers.length}
                onReset={resetFilters}
                rightSlot={
                    <Button onClick={() => setOpenAddDialog(true)}>
                        <Plus size={16} />
                        Người dùng mới
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
                                <TableHead className="px-4 py-3">ID</TableHead>
                                <TableHead className="px-4 py-3">Họ tên</TableHead>
                                <TableHead className="px-4 py-3">Tên đăng nhập</TableHead>
                                <TableHead className="px-4 py-3">Email</TableHead>
                                <TableHead className="px-4 py-3">Vai trò</TableHead>
                                <TableHead className="px-4 py-3">Đơn vị</TableHead>
                                <TableHead className="px-4 py-3">Trạng thái</TableHead>
                                <TableHead className="px-4 py-3">Đăng nhập cuối</TableHead>
                                <TableHead className="px-4 py-3 text-right">Hành động</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading && (
                                <TableRow>
                                    <TableCell colSpan={9} className="px-4 py-6 text-center text-sm text-gray-400">
                                        Đang tải dữ liệu...
                                    </TableCell>
                                </TableRow>
                            )}

                            {!loading && filteredUsers.map((user) => (
                                <TableRow key={user.user_id} className="transition hover:bg-blue-50/60">
                                    <TableCell className="max-w-32 truncate px-4 py-3 text-gray-500" title={user.user_id}>
                                        {user.user_id}
                                    </TableCell>
                                    <TableCell className="px-4 py-3 font-medium text-gray-900">{user.full_name}</TableCell>
                                    <TableCell className="px-4 py-3 text-gray-600">{user.username}</TableCell>
                                    <TableCell className="px-4 py-3 text-gray-600">{user.email}</TableCell>
                                    <TableCell className="px-4 py-3 text-gray-600">{roleMap[user.role_id] ?? '-'}</TableCell>
                                    <TableCell className="px-4 py-3 text-gray-600">
                                        {user.department_id ? departmentMap[user.department_id] ?? '-' : '-'}
                                    </TableCell>
                                    <TableCell className="px-4 py-3">
                                        <span className="inline-flex items-center gap-1.5 text-sm text-gray-700">
                                            <span
                                                className={`h-2.5 w-2.5 rounded-full ${user.status === 'active' ? 'bg-green-500' : 'bg-red-500'}`}
                                            />
                                            {user.status === 'active' ? 'Hoạt động' : 'Đã khoá'}
                                        </span>
                                    </TableCell>
                                    <TableCell className="px-4 py-3 text-gray-600">{formatDateTime(user.last_login_at)}</TableCell>
                                    <TableCell className="px-4 py-3 text-right">
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Button variant="ghost" size="icon" aria-label="Mở menu hành động">
                                                    <MoreHorizontal size={16} />
                                                </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                                <DropdownMenuItem onClick={() => setEditingUser(user)}>
                                                    Sửa thông tin
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onClick={() => handleToggleStatus(user)}>
                                                    {user.status === 'active' ? 'Vô hiệu hoá' : 'Kích hoạt'}
                                                </DropdownMenuItem>
                                                <DropdownMenuItem variant="destructive" onClick={() => setDeletingUser(user)}>
                                                    Xoá
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </TableCell>
                                </TableRow>
                            ))}

                            {!loading && filteredUsers.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={9} className="px-4 py-10 text-center text-sm text-gray-400">
                                        Không có dữ liệu
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </div>
            </div>

            <AddUserDialog
                open={openAddDialog}
                onOpenChange={setOpenAddDialog}
                roles={roles}
                departments={departments}
                onCreated={(user) => setUsers((prev) => [user, ...prev])}
            />

            <EditUserDialog
                open={!!editingUser}
                onOpenChange={(open) => !open && setEditingUser(null)}
                user={editingUser}
                roles={roles}
                departments={departments}
                onUpdated={(updated) => setUsers((prev) => prev.map((u) => (u.user_id === updated.user_id ? updated : u)))}
            />

            <DeleteUserAlert
                open={!!deletingUser}
                onOpenChange={(open) => !open && setDeletingUser(null)}
                user={deletingUser}
                onDeleted={(userId) => setUsers((prev) => prev.filter((u) => u.user_id !== userId))}
            />
        </div>
    )
}
