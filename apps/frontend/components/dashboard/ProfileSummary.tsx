'use client'

import { LogOut, ShieldCheck, UserRound } from 'lucide-react'

import { Button } from '@/components/ui/button'

type ProfileSummaryUser = {
    full_name: string
    username: string
    email: string
    role_name: string
    department_name?: string | null
}

type ProfileSummaryProps = {
    title: string
    description: string
    user: ProfileSummaryUser
    onLogout: () => void
}

export default function ProfileSummary({ title, description, user, onLogout }: ProfileSummaryProps) {
    return (
        <div className="space-y-6 p-6">
            <div className="flex flex-wrap items-end justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
                    <p className="mt-1 text-sm text-gray-500">{description}</p>
                </div>

                <Button variant="outline" onClick={onLogout}>
                    <LogOut size={16} />
                    Đăng xuất
                </Button>
            </div>

            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                <div className="border-b border-gray-100 bg-gray-50 px-5 py-4">
                    <div className="flex items-center gap-3">
                        <div className="flex size-9 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-600">
                            <UserRound size={18} />
                        </div>
                        <div>
                            <h2 className="text-sm font-semibold text-gray-900">Thông tin người dùng</h2>
                            <p className="text-xs text-gray-500">Thông tin tài khoản đang đăng nhập</p>
                        </div>
                    </div>
                </div>

                <dl className="grid gap-0 divide-y divide-gray-100 text-sm sm:grid-cols-2 sm:divide-x sm:divide-y-0">
                    <div className="space-y-1 p-5">
                        <dt className="text-xs font-medium uppercase text-gray-400">Họ tên</dt>
                        <dd className="font-medium text-gray-900">{user.full_name}</dd>
                    </div>
                    <div className="space-y-1 p-5">
                        <dt className="text-xs font-medium uppercase text-gray-400">Tên đăng nhập</dt>
                        <dd className="text-gray-700">{user.username}</dd>
                    </div>
                    <div className="space-y-1 p-5">
                        <dt className="text-xs font-medium uppercase text-gray-400">Email</dt>
                        <dd className="text-gray-700">{user.email}</dd>
                    </div>
                    <div className="space-y-1 p-5">
                        <dt className="text-xs font-medium uppercase text-gray-400">Vai trò</dt>
                        <dd className="inline-flex items-center gap-2 text-gray-700">
                            <ShieldCheck size={15} className="text-gray-400" />
                            {user.role_name}
                        </dd>
                    </div>
                    {user.department_name && (
                        <div className="space-y-1 p-5 sm:col-span-2">
                            <dt className="text-xs font-medium uppercase text-gray-400">Phòng ban</dt>
                            <dd className="text-gray-700">{user.department_name}</dd>
                        </div>
                    )}
                </dl>
            </div>
        </div>
    )
}
