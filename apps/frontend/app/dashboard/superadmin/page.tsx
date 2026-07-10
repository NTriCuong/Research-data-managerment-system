'use client'

import { useAppDispatch, useAppSelector } from '@/lib/hooks/hooks'
import { selectCurrentUser } from '@/store/slice/auth.slice'
import { useRouter } from 'next/navigation'
import StatCard from '@/components/report/StatCard'
import { BookOpen, Clock, Layers, Users } from 'lucide-react'
import { useEffect, useState } from 'react'
import { PendingStatus, reportService, StatusBreakdownItem, TopDepartmentItem, TotalCoreRepositories, TotalResearchers } from '@/services/reports/report.service'
import StatusBreakdownCard from '@/components/report/StatusBreakdownCard'
import TopDepartmentsCard from '@/components/report/TopDepartmentCard'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { toast } from 'sonner'
import { referenceService } from '@/services/reference/reference.service'
import RecentLoginLogs from '@/components/superadmin/RecentLoginLogs'
import RecentAuditLogs from '@/components/superadmin/RecentAuditLogs'


export default function SuperAdminPage() {
    const currentUser = useAppSelector(selectCurrentUser)
    const dispatch = useAppDispatch()
    const router = useRouter()

    const [totalRepos, setTotalRepos] = useState<TotalCoreRepositories | null>(null)
    const [pending, setPending] = useState<PendingStatus | null>(null)
    const [researchers, setResearchers] = useState<TotalResearchers | null>(null)
    const [breakdown, setBreakdown] = useState<StatusBreakdownItem[]>([])
    const [topDepts, setTopDepts] = useState<TopDepartmentItem[]>([])
    const [loading, setLoading] = useState(true)
    const [outPutType, setOutPutType] = useState(0)


    const fetchAll = async (isRefresh = false) => {
        setLoading(true)
        try {
            const [repos, pend, resrc, qual, bkdn, depts] = await Promise.all([
                reportService.getTotalCoreRepositories(),
                reportService.getPendingStatus(),
                reportService.getTotalResearchers(),
                reportService.getMetadataQuality(),
                reportService.getStatusBreakdown(),
                reportService.getTopDepartments(10),
            ])
            setTotalRepos(repos)
            setPending(pend)
            setResearchers(resrc)
            setBreakdown(bkdn)
            setTopDepts(depts)
            // output type
            const opt = referenceService.getOutputTypes();
            console.log(opt);
            setOutPutType(outPutType)
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { fetchAll() }, [])


    if (!currentUser) {
        return <p className="p-6 text-sm text-gray-500">Đang tải dữ liệu...</p>
    }

    return (
        <div className="space-y-6 p-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900">Tổng quan</h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Thống kê tổng quan hoạt động của hệ thống.
                    </p>
                </div>
            </div>

            {/* Stat cards */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <StatCard
                    icon={BookOpen}
                    label="Công trình đã duyệt"
                    value={totalRepos?.total_core_repositories ?? 0}
                    sub="Trong Core"
                    iconColor="bg-blue-500"
                    loading={loading}
                />
                <StatCard
                    icon={Clock}
                    label="Đang chờ xử lý"
                    value={pending?.total_pending ?? 0}
                    sub={pending ? `Xét duyệt: ${pending.pending_review} · Phê duyệt: ${pending.pending_approval}` : undefined}
                    iconColor="bg-yellow-500"
                    loading={loading}
                />
                <StatCard
                    icon={Users}
                    label="Nhà nghiên cứu"
                    value={researchers?.total_researchers ?? 0}
                    sub={researchers ? `Nội bộ: ${researchers.internal} · Bên ngoài: ${researchers.external}` : undefined}
                    iconColor="bg-purple-500"
                    loading={loading}
                />

                <StatCard
                    icon={Layers}
                    label="Loại sản phẩm nghiên cứu"
                    value={pending?.total_pending ?? 0}
                    sub={pending ? `Xét duyệt: ${pending.pending_review} · Phê duyệt: ${pending.pending_approval}` : undefined}
                    iconColor="bg-yellow-800"
                    loading={loading}
                />
            </div>

            {/* Status breakdown + top departments */}
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <StatusBreakdownCard items={breakdown} loading={loading} />
                <TopDepartmentsCard items={topDepts} loading={loading} />
            </div>
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <RecentLoginLogs />
                <RecentAuditLogs />
            </div>
        </div>
    )
}
