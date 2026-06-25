import { UserRoundSearch } from 'lucide-react'

import DashboardPlaceholder from '@/components/dashboard/DashboardPlaceholder'

export default function SuperAdminResearchersPage() {
    return (
        <DashboardPlaceholder
            title="Nhà nghiên cứu"
            description="Quản lý hồ sơ tác giả, cộng tác viên và thông tin liên hệ."
            icon={UserRoundSearch}
        />
    )
}
