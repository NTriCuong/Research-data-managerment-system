'use client'

import ProfileSummary from '@/components/dashboard/ProfileSummary'
import { authService } from '@/services/auth/auth.service'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { selectCurrentUser } from '@/store/slice/auth.slice'
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
        return <p className="p-6 text-sm text-gray-500">Đang tải dữ liệu...</p>
    }

    return (
        <ProfileSummary
            title="Kiểm duyệt"
            description="Xem nhanh thông tin tài khoản và điều hướng sang danh sách chờ kiểm duyệt."
            user={currentUser}
            onLogout={handleLogout}
        />
    )
}
