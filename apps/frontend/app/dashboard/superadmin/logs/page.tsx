import { ScrollText } from 'lucide-react'

import DashboardPlaceholder from '@/components/dashboard/DashboardPlaceholder'

export default function SuperAdminLogsPage() {
    return (
        <DashboardPlaceholder
            title="Nhật ký hệ thống"
            description="Theo dõi các hoạt động quản trị và thay đổi dữ liệu quan trọng."
            icon={ScrollText}
        />
    )
}
