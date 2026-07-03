'use client'

import { useEffect, useState } from 'react'
import { Search, RotateCcw } from 'lucide-react'
import { toast } from 'sonner'

import { logService, type WorkflowLog } from '@/services/logs/log.service'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'

function formatDt(v: string) {
    return new Date(v).toLocaleString('vi-VN')
}

const STATUS_MAP: Record<string, { label: string; bar: string; badge: string }> = {
    draft:             { label: 'Bản nháp',      bar: 'bg-gray-400',   badge: 'bg-gray-100 text-gray-600' },
    pending_review:    { label: 'Chờ duyệt',     bar: 'bg-yellow-500', badge: 'bg-yellow-100 text-yellow-700' },
    revision_required: { label: 'Yêu cầu sửa',   bar: 'bg-orange-500', badge: 'bg-orange-100 text-orange-700' },
    approved:          { label: 'Đã duyệt',      bar: 'bg-green-500',  badge: 'bg-green-100 text-green-700' },
    rejected:          { label: 'Từ chối',       bar: 'bg-red-500',    badge: 'bg-red-100 text-red-700' },
    published:         { label: 'Đã xuất bản',   bar: 'bg-blue-500',   badge: 'bg-blue-100 text-blue-700' },
}

function StatusBadge({ status }: { status: string | null }) {
    if (!status) return <span className="text-xs text-gray-400">-</span>
    const cfg = STATUS_MAP[status]
    return (
        <Badge variant="secondary" className={`${cfg?.badge ?? 'bg-gray-100 text-gray-600'} hover:opacity-90`}>
            {cfg?.label ?? status}
        </Badge>
    )
}

function workflowColorBar(toStatus: string) {
    return STATUS_MAP[toStatus]?.bar ?? 'bg-gray-400'
}

export default function WorkflowLogTab() {
    const [actionCode, setActionCode] = useState('')
    const [performedFrom, setPerformedFrom] = useState('')
    const [performedTo, setPerformedTo] = useState('')
    const [logs, setLogs] = useState<WorkflowLog[]>([])
    const [loading, setLoading] = useState(false)

    const fetchLogs = async (params?: Record<string, string | undefined>) => {
        setLoading(true)
        try {
            const data = await logService.listWorkflowLogs({ limit: 100, ...params })
            setLogs(data)
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { fetchLogs() }, [])

    const handleSearch = () => fetchLogs({
        action_code: actionCode.trim() || undefined,
        performed_from: performedFrom ? `${performedFrom}T00:00:00` : undefined,
        performed_to: performedTo ? `${performedTo}T23:59:59` : undefined,
    })

    const handleReset = () => {
        setActionCode('')
        setPerformedFrom('')
        setPerformedTo('')
        fetchLogs()
    }

    return (
        <div className="space-y-4">
            <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
                    <div className="space-y-1">
                        <Label className="text-xs text-gray-500">Mã hành động</Label>
                        <Input
                            placeholder="SUBMIT_FOR_REVIEW, APPROVE..."
                            value={actionCode}
                            onChange={(e) => setActionCode(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                            className="h-8 text-sm"
                        />
                    </div>
                    <div className="space-y-1">
                        <Label className="text-xs text-gray-500">Từ ngày</Label>
                        <Input type="date" value={performedFrom} onChange={(e) => setPerformedFrom(e.target.value)} className="h-8 text-sm" />
                    </div>
                    <div className="space-y-1">
                        <Label className="text-xs text-gray-500">Đến ngày</Label>
                        <Input type="date" value={performedTo} onChange={(e) => setPerformedTo(e.target.value)} className="h-8 text-sm" />
                    </div>
                </div>
                <div className="mt-3 flex items-center gap-2">
                    <Button size="sm" onClick={handleSearch} disabled={loading}>
                        <Search size={14} />
                        Tìm kiếm
                    </Button>
                    <Button size="sm" variant="outline" onClick={handleReset} disabled={loading}>
                        <RotateCcw size={14} />
                        Đặt lại
                    </Button>
                    <span className="ml-2 text-xs text-gray-400">{logs.length} bản ghi</span>
                </div>
            </div>

            {/* Chú thích màu */}
            <div className="flex flex-wrap items-center gap-3 px-1">
                {Object.entries(STATUS_MAP).map(([, { label, bar }]) => (
                    <span key={label} className="flex items-center gap-1.5 text-xs text-gray-500">
                        <span className={`inline-block h-3 w-1 rounded-sm ${bar}`} />
                        {label}
                    </span>
                ))}
            </div>

            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                <div className="max-h-[calc(100vh-380px)] overflow-auto">
                    <Table className="min-w-max">
                        <TableHeader className="sticky top-0 z-10 bg-gray-50 text-xs uppercase tracking-wide text-gray-500">
                            <TableRow className="hover:bg-transparent">
                                <TableHead className="w-1 p-0" />
                                <TableHead className="px-4 py-3">Thời gian</TableHead>
                                <TableHead className="px-4 py-3">Mã hành động</TableHead>
                                <TableHead className="px-4 py-3">Trạng thái trước</TableHead>
                                <TableHead className="px-4 py-3">Trạng thái sau</TableHead>
                                <TableHead className="px-4 py-3">Ghi chú</TableHead>
                                <TableHead className="px-4 py-3">Staging ID</TableHead>
                                <TableHead className="px-4 py-3">Research ID</TableHead>
                                <TableHead className="px-4 py-3">Địa chỉ IP</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading && (
                                <TableRow>
                                    <TableCell colSpan={9} className="py-6 text-center text-sm text-gray-400">
                                        Đang tải dữ liệu...
                                    </TableCell>
                                </TableRow>
                            )}
                            {!loading && logs.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={9} className="py-10 text-center text-sm text-gray-400">
                                        Không có dữ liệu
                                    </TableCell>
                                </TableRow>
                            )}
                            {!loading && logs.map((log) => (
                                <TableRow key={log.workflow_id} className="hover:bg-gray-50/60">
                                    <TableCell className={`w-1 p-0 ${workflowColorBar(log.to_status)}`} />
                                    <TableCell className="whitespace-nowrap px-4 py-2.5 text-xs text-gray-500">
                                        {formatDt(log.performed_at)}
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5">
                                        <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-700">
                                            {log.action_code}
                                        </code>
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5">
                                        <StatusBadge status={log.from_status} />
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5">
                                        <StatusBadge status={log.to_status} />
                                    </TableCell>
                                    <TableCell className="max-w-48 truncate px-4 py-2.5 text-xs text-gray-600" title={log.action_note ?? ''}>
                                        {log.action_note || <span className="text-gray-400">-</span>}
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5 font-mono text-xs text-gray-400" title={log.staging_id ?? ''}>
                                        {log.staging_id ? log.staging_id.slice(0, 8) + '...' : '-'}
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5 font-mono text-xs text-gray-400" title={log.research_id ?? ''}>
                                        {log.research_id ? log.research_id.slice(0, 8) + '...' : '-'}
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5 text-xs text-gray-400">
                                        {log.ip_address || '-'}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            </div>
        </div>
    )
}
