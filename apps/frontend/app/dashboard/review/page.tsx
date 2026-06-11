
'use client'

import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { selectCurrentUser } from '@/store/slice/auth.slice'
import { authService } from '@/services/auth/auth.service'
import { useRouter } from 'next/navigation'

export default function ReviewPage() {
    const currentUser = useAppSelector(selectCurrentUser)
    const dispatch = useAppDispatch()
    const router = useRouter()

    const handleLogout = async () => {
        await authService.logout(dispatch)
        router.replace('/login')
    }

    if (!currentUser) {
        return <p>Loading...</p>
    }

    return (
        <div className="p-6">
            <div className="flex items-center justify-between mb-4">
                <h1 className="text-2xl font-bold">Review</h1>
                <button
                    onClick={handleLogout}
                    className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                >
                    Đăng xuất
                </button>
            </div>
            <div className="bg-white rounded-lg shadow p-6 max-w-md">
                <h2 className="text-lg font-semibold mb-4">Thông tin người dùng</h2>
                <dl className="space-y-2">
                    <div className="flex gap-2">
                        <dt className="font-medium text-gray-500 w-36">Họ tên:</dt>
                        <dd>{currentUser.full_name}</dd>
                    </div>
                    <div className="flex gap-2">
                        <dt className="font-medium text-gray-500 w-36">Tên đăng nhập:</dt>
                        <dd>{currentUser.username}</dd>
                    </div>
                    <div className="flex gap-2">
                        <dt className="font-medium text-gray-500 w-36">Email:</dt>
                        <dd>{currentUser.email}</dd>
                    </div>
                    <div className="flex gap-2">
                        <dt className="font-medium text-gray-500 w-36">Vai trò:</dt>
                        <dd>{currentUser.role_name}</dd>
                    </div>
                    {currentUser.department_name && (
                        <div className="flex gap-2">
                            <dt className="font-medium text-gray-500 w-36">Phòng ban:</dt>
                            <dd>{currentUser.department_name}</dd>
                        </div>
                    )}
                </dl>
            </div>
        </div>
    );
}
