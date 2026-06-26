'use client'

import ProfileSummary from '@/components/dashboard/ProfileSummary'
import { authService } from '@/services/auth/auth.service'
import { useAppDispatch, useAppSelector } from '@/lib/hooks/hooks'
import { selectCurrentUser } from '@/store/slice/auth.slice'
import { useRouter } from 'next/navigation'

export default function ReportsPage() {
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
            title="Báo cáo"
            description="Khu vực báo cáo dùng chung theo quyền truy cập hiện tại."
            user={currentUser}
            onLogout={handleLogout}
        />
    )
}
