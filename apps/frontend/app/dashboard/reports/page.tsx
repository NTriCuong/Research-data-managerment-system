'use client'

import { useEffect, useState } from 'react'
import { BarChart3, BookOpen, Clock, Users, Star, Building2, RefreshCw } from 'lucide-react'
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

// ─── Trạng thái workflow ──────────────────────────────────────────────────────
const STATUS_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
    draft: { label: 'Bản nháp', color: 'bg-gray-400', bg: 'bg-gray-50' },
    pending_review: { label: 'Chờ xét duyệt', color: 'bg-yellow-400', bg: 'bg-yellow-50' },
    revision_required: { label: 'Yêu cầu sửa', color: 'bg-orange-400', bg: 'bg-orange-50' },
    approved: { label: 'Đã duyệt', color: 'bg-green-500', bg: 'bg-green-50' },
    rejected: { label: 'Từ chối', color: 'bg-red-500', bg: 'bg-red-50' },
    published: { label: 'Đã xuất bản', color: 'bg-blue-500', bg: 'bg-blue-50' },
}

// ─── Stat card ────────────────────────────────────────────────────────────────
function StatCard({
    icon: Icon,
    label,
    value,
    sub,
    iconColor,
    loading,
}: {
    icon: React.ElementType
    label: string
    value: string | number
    sub?: string
    iconColor: string
    loading: boolean
}) {
    return (
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm text-gray-500">{label}</p>
                    {loading ? (
                        <div className="mt-2 h-8 w-24 animate-pulse rounded bg-gray-100" />
                    ) : (
                        <p className="mt-1 text-3xl font-bold text-gray-900">{value}</p>
                    )}
                    {sub && !loading && (
                        <p className="mt-1 text-xs text-gray-400">{sub}</p>
                    )}
                </div>
                <div className={`rounded-lg p-2.5 ${iconColor}`}>
                    <Icon size={20} className="text-white" />
                </div>
            </div>
        </div>
    )
}

// ─── Status breakdown bar ─────────────────────────────────────────────────────
function StatusBreakdownCard({ items, loading }: { items: StatusBreakdownItem[]; loading: boolean }) {
    const total = items.reduce((s, i) => s + i.count, 0)

    return (
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
                <BarChart3 size={16} className="text-gray-400" />
                <h3 className="text-sm font-semibold text-gray-700">Phân bổ trạng thái</h3>
            </div>

            {loading ? (
                <div className="space-y-3">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="h-8 animate-pulse rounded bg-gray-100" />
                    ))}
                </div>
            ) : total === 0 ? (
                <p className="py-6 text-center text-sm text-gray-400">Không có dữ liệu</p>
            ) : (
                <div className="space-y-3">
                    {/* Combined progress bar */}
                    <div className="flex h-3 w-full overflow-hidden rounded-full">
                        {items.map((item) => {
                            const cfg = STATUS_CONFIG[item.status]
                            const pct = total > 0 ? (item.count / total) * 100 : 0
                            return (
                                <div
                                    key={item.status}
                                    className={`${cfg?.color ?? 'bg-gray-300'} transition-all`}
                                    style={{ width: `${pct}%` }}
                                    title={`${cfg?.label ?? item.status}: ${item.count}`}
                                />
                            )
                        })}
                    </div>

                    {/* List */}
                    <div className="space-y-2 pt-1">
                        {items.map((item) => {
                            const cfg = STATUS_CONFIG[item.status]
                            const pct = total > 0 ? ((item.count / total) * 100).toFixed(1) : '0'
                            return (
                                <div key={item.status} className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <span className={`inline-block h-2.5 w-2.5 rounded-full ${cfg?.color ?? 'bg-gray-300'}`} />
                                        <span className="text-xs text-gray-600">{cfg?.label ?? item.status}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="h-1.5 w-24 overflow-hidden rounded-full bg-gray-100">
                                            <div
                                                className={`h-full ${cfg?.color ?? 'bg-gray-300'}`}
                                                style={{ width: `${pct}%` }}
                                            />
                                        </div>
                                        <span className="w-16 text-right text-xs text-gray-500">
                                            {item.count} ({pct}%)
                                        </span>
                                    </div>
                                </div>
                            )
                        })}
                    </div>

                    <p className="border-t border-gray-100 pt-2 text-right text-xs text-gray-400">
                        Tổng: {total} bản ghi
                    </p>
                </div>
            )}
        </div>
    )
}

// ─── Top departments table ────────────────────────────────────────────────────
function TopDepartmentsCard({ items, loading }: { items: TopDepartmentItem[]; loading: boolean }) {
    const max = items[0]?.count ?? 1

    return (
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
                <Building2 size={16} className="text-gray-400" />
                <h3 className="text-sm font-semibold text-gray-700">Đơn vị đóng góp nhiều nhất</h3>
            </div>

            {loading ? (
                <div className="space-y-3">
                    {[1, 2, 3, 4, 5].map((i) => (
                        <div key={i} className="h-8 animate-pulse rounded bg-gray-100" />
                    ))}
                </div>
            ) : items.length === 0 ? (
                <p className="py-6 text-center text-sm text-gray-400">Không có dữ liệu</p>
            ) : (
                <div className="space-y-2.5">
                    {items.map((dept, idx) => (
                        <div key={dept.department_name} className="flex items-center gap-3">
                            <span className="w-5 text-right text-xs font-medium text-gray-400">
                                {idx + 1}
                            </span>
                            <div className="min-w-0 flex-1">
                                <div className="mb-1 flex items-center justify-between">
                                    <span className="truncate text-xs font-medium text-gray-700">
                                        {dept.department_name}
                                    </span>
                                    <span className="ml-2 shrink-0 text-xs text-gray-500">
                                        {dept.count}
                                    </span>
                                </div>
                                <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
                                    <div
                                        className="h-full rounded-full bg-blue-500 transition-all duration-500"
                                        style={{ width: `${(dept.count / max) * 100}%` }}
                                    />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

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
