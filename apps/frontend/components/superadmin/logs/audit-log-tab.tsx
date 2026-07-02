'use client'

import { useEffect, useState } from 'react'
import { Search, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react'
import { toast } from 'sonner'

import { logService, type AuditLog } from '@/services/logs/log.service'
import { parseAxiosError } from '@/lib/axios/error-paser'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'

function formatDt(v: string) {
    return new Date(v).toLocaleString('vi-VN')
}

function JsonCell({ data }: { data: Record<string, unknown> | null }) {
    const [open, setOpen] = useState(false)
    if (!data) return <span className="italic text-xs text-gray-400">-</span>
    return (
        <div className="max-w-48">
            <button
                onClick={() => setOpen((v) => !v)}
                className="flex items-center gap-1 text-xs text-blue-600 hover:underline"
            >
                {Object.keys(data).length} trường
                {open ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
            {open && (
                <pre className="mt-1 max-h-40 overflow-auto rounded bg-gray-50 p-2 text-xs text-gray-700">
                    {JSON.stringify(data, null, 2)}
                </pre>
            )}
        </div>
    )
}

const colorBar = (success: boolean) =>
    success ? 'bg-green-500' : 'bg-red-500'

export default function AuditLogTab() {
    const [actionCode, setActionCode] = useState('')
    const [result, setResult] = useState('')
    const [targetTable, setTargetTable] = useState('')
    const [createdFrom, setCreatedFrom] = useState('')
    const [createdTo, setCreatedTo] = useState('')
    const [logs, setLogs] = useState<AuditLog[]>([])
    const [loading, setLoading] = useState(false)

    const fetchLogs = async (params?: Record<string, string | undefined>) => {
        setLoading(true)
        try {
            const data = await logService.listAuditLogs({ limit: 100, ...params })
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
        result: result || undefined,
        target_table: targetTable.trim() || undefined,
        created_from: createdFrom ? `${createdFrom}T00:00:00` : undefined,
        created_to: createdTo ? `${createdTo}T23:59:59` : undefined,
    })

    const handleReset = () => {
        setActionCode('')
        setResult('')
        setTargetTable('')
        setCreatedFrom('')
        setCreatedTo('')
        fetchLogs()
    }

    return (
        <div className="space-y-4">
            {/* Bộ lọc */}
            <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-5">
                    <div className="space-y-1">
                        <Label className="text-xs text-gray-500">Mã hành động</Label>
                        <Input
                            placeholder="CREATE_USER, DELETE_DEPT..."
                            value={actionCode}
                            onChange={(e) => setActionCode(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                            className="h-8 text-sm"
                        />
                    </div>
                    <div className="space-y-1">
                        <Label className="text-xs text-gray-500">Kết quả</Label>
                        <Select value={result} onValueChange={setResult}>
                            <SelectTrigger className="h-8 text-sm">
                                <SelectValue placeholder="Tất cả" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="success">Thành công</SelectItem>
                                <SelectItem value="failure">Thất bại</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="space-y-1">
                        <Label className="text-xs text-gray-500">Bảng đích</Label>
                        <Input
                            placeholder="users, departments..."
                            value={targetTable}
                            onChange={(e) => setTargetTable(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                            className="h-8 text-sm"
                        />
                    </div>
                    <div className="space-y-1">
                        <Label className="text-xs text-gray-500">Từ ngày</Label>
                        <Input type="date" value={createdFrom} onChange={(e) => setCreatedFrom(e.target.value)} className="h-8 text-sm" />
                    </div>
                    <div className="space-y-1">
                        <Label className="text-xs text-gray-500">Đến ngày</Label>
                        <Input type="date" value={createdTo} onChange={(e) => setCreatedTo(e.target.value)} className="h-8 text-sm" />
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

            {/* Bảng dữ liệu */}
            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                <div className="max-h-[calc(100vh-340px)] overflow-auto">
                    <Table className="min-w-max">
                        <TableHeader className="sticky top-0 z-10 bg-gray-50 text-xs uppercase tracking-wide text-gray-500">
                            <TableRow className="hover:bg-transparent">
                                <TableHead className="w-1 p-0" />
                                <TableHead className="px-4 py-3">Thời gian</TableHead>
                                <TableHead className="px-4 py-3">Mã hành động</TableHead>
                                <TableHead className="px-4 py-3">Bảng đích</TableHead>
                                <TableHead className="px-4 py-3">ID đối tượng</TableHead>
                                <TableHead className="px-4 py-3">Nội dung</TableHead>
                                <TableHead className="px-4 py-3">Dữ liệu cũ</TableHead>
                                <TableHead className="px-4 py-3">Dữ liệu mới</TableHead>
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
                                <TableRow key={log.audit_id} className="hover:bg-gray-50/60">
                                    <TableCell className={`w-1 p-0 ${colorBar(log.result === 'success')}`} />
                                    <TableCell className="whitespace-nowrap px-4 py-2.5 text-xs text-gray-500">
                                        {formatDt(log.created_at)}
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5">
                                        <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-700">
                                            {log.action_code}
                                        </code>
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5 text-xs text-gray-600">
                                        {log.target_table
                                            ? <span className="font-mono">{log.target_schema}.{log.target_table}</span>
                                            : <span className="text-gray-400">-</span>
                                        }
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5 font-mono text-xs text-gray-400" title={log.target_id ?? ''}>
                                        {log.target_id ? log.target_id.slice(0, 8) + '...' : '-'}
                                    </TableCell>
                                    <TableCell className="max-w-56 truncate px-4 py-2.5 text-xs text-gray-600" title={log.message ?? ''}>
                                        {log.message || <span className="text-gray-400">-</span>}
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5">
                                        <JsonCell data={log.old_value} />
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5">
                                        <JsonCell data={log.new_value} />
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
