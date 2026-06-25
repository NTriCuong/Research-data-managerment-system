import { FileText } from 'lucide-react'

import DashboardPlaceholder from '@/components/dashboard/DashboardPlaceholder'

export default function SuperAdminResearchesPage() {
    return (
        <DashboardPlaceholder
            title="Kho nghiên cứu"
            description="Theo dõi các bản ghi nghiên cứu đã được duyệt vào hệ thống."
            icon={FileText}
        />
    )
}
