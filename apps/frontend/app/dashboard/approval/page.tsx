'use client'

import ProfileSummary from '@/components/dashboard/ProfileSummary'
import { authService } from '@/services/auth/auth.service'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { selectCurrentUser } from '@/store/slice/auth.slice'
import { useRouter } from 'next/navigation'

export default function ApprovalPage() {
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
            title="Phê duyệt"
            description="Theo dõi hồ sơ nghiên cứu đang chờ phê duyệt."
            user={currentUser}
            onLogout={handleLogout}
        />
    )
}
