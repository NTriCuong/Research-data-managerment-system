import { Building2 } from 'lucide-react'

import DashboardPlaceholder from '@/components/dashboard/DashboardPlaceholder'

export default function SuperAdminDepartmentsPage() {
    return (
        <DashboardPlaceholder
            title="Quản lý đơn vị"
            description="Danh sách phòng ban, khoa và đơn vị tham gia nghiên cứu."
            icon={Building2}
        />
    )
}
