'use client'

import { useEffect, useState } from 'react'
import { BookOpen, Clock, Users, Star, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'

import {
    reportService,
    type TotalCoreRepositories,
    type PendingStatus,
    type TotalResearchers,
    type MetadataQuality,
    type StatusBreakdownItem,
    type TopDepartmentItem,
} from '@/services/reports/report.service'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { Button } from '@/components/ui/button'
import StatCard from '@/components/report/StatCard'
import StatusBreakdownCard from '@/components/report/StatusBreakdownCard'
import TopDepartmentsCard from '@/components/report/TopDepartmentCard'



// ─── Main page ────────────────────────────────────────────────────────────────
export default function ReportsPage() {
    const [totalRepos, setTotalRepos] = useState<TotalCoreRepositories | null>(null)
    const [pending, setPending] = useState<PendingStatus | null>(null)
    const [researchers, setResearchers] = useState<TotalResearchers | null>(null)
    const [quality, setQuality] = useState<MetadataQuality | null>(null)
    const [breakdown, setBreakdown] = useState<StatusBreakdownItem[]>([])
    const [topDepts, setTopDepts] = useState<TopDepartmentItem[]>([])
    const [loading, setLoading] = useState(true)
    const [refreshing, setRefreshing] = useState(false)

    const fetchAll = async (isRefresh = false) => {
        if (isRefresh) setRefreshing(true)
        else setLoading(true)
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
            setQuality(qual)
            setBreakdown(bkdn)
            setTopDepts(depts)
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setLoading(false)
            setRefreshing(false)
        }
    }

    useEffect(() => { fetchAll() }, [])

    return (
        <div className="space-y-6 p-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900">Báo cáo tổng quan</h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Thống kê hoạt động nghiên cứu và chất lượng dữ liệu.
                    </p>
                </div>
                <Button
                    size="sm"
                    variant="outline"
                    onClick={() => fetchAll(true)}
                    disabled={loading || refreshing}
                >
                    <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} />
                    Làm mới
                </Button>
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
                    icon={Star}
                    label="Chất lượng metadata"
                    value={quality ? `${Math.round(quality.avg_score)}/100` : '—'}
                    sub={quality ? `Trên ${quality.total_records} bản ghi` : undefined}
                    iconColor="bg-green-500"
                    loading={loading}
                />
            </div>

            {/* Status breakdown + top departments */}
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <StatusBreakdownCard items={breakdown} loading={loading} />
                <TopDepartmentsCard items={topDepts} loading={loading} />
            </div>
        </div>
    )
}
