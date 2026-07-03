'use client'

import { useEffect, useState } from 'react'
import { Search, RotateCcw } from 'lucide-react'
import { toast } from 'sonner'

import { logService, type LoginLog } from '@/services/logs/log.service'
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

const colorBar = (success: boolean) =>
    success ? 'bg-green-500' : 'bg-red-500'

export default function LoginLogTab() {
    const [username, setUsername] = useState('')
    const [loginResult, setLoginResult] = useState('')
    const [createdFrom, setCreatedFrom] = useState('')
    const [createdTo, setCreatedTo] = useState('')
    const [logs, setLogs] = useState<LoginLog[]>([])
    const [loading, setLoading] = useState(false)

    const fetchLogs = async (params?: Record<string, string | undefined>) => {
        setLoading(true)
        try {
            const data = await logService.listLoginLogs({ limit: 100, ...params })
            setLogs(data)
        } catch (err) {
            toast.error(parseAxiosError(err).message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { fetchLogs() }, [])

    const handleSearch = () => fetchLogs({
        username: username.trim() || undefined,
        login_result: loginResult || undefined,
        created_from: createdFrom ? `${createdFrom}T00:00:00` : undefined,
        created_to: createdTo ? `${createdTo}T23:59:59` : undefined,
    })

    const handleReset = () => {
        setUsername('')
        setLoginResult('')
        setCreatedFrom('')
        setCreatedTo('')
        fetchLogs()
    }

    return (
        <div className="space-y-4">
            <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                    <div className="space-y-1">
                        <Label className="text-xs text-gray-500">Tên đăng nhập</Label>
                        <Input
                            placeholder="Tìm theo tên đăng nhập..."
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                            className="h-8 text-sm"
                        />
                    </div>
                    <div className="space-y-1">
                        <Label className="text-xs text-gray-500">Kết quả</Label>
                        <Select value={loginResult} onValueChange={setLoginResult}>
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

            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
                <div className="max-h-[calc(100vh-340px)] overflow-auto">
                    <Table className="min-w-max">
                        <TableHeader className="sticky top-0 z-10 bg-gray-50 text-xs uppercase tracking-wide text-gray-500">
                            <TableRow className="hover:bg-transparent">
                                <TableHead className="w-1 p-0" />
                                <TableHead className="px-4 py-3">Thời gian</TableHead>
                                <TableHead className="px-4 py-3">Tên đăng nhập</TableHead>
                                <TableHead className="px-4 py-3">Lý do thất bại</TableHead>
                                <TableHead className="px-4 py-3">Địa chỉ IP</TableHead>
                                <TableHead className="px-4 py-3">Thiết bị</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading && (
                                <TableRow>
                                    <TableCell colSpan={6} className="py-6 text-center text-sm text-gray-400">
                                        Đang tải dữ liệu...
                                    </TableCell>
                                </TableRow>
                            )}
                            {!loading && logs.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={6} className="py-10 text-center text-sm text-gray-400">
                                        Không có dữ liệu
                                    </TableCell>
                                </TableRow>
                            )}
                            {!loading && logs.map((log) => (
                                <TableRow key={log.login_log_id} className="hover:bg-gray-50/60">
                                    <TableCell className={`w-1 p-0 ${colorBar(log.login_result === 'success')}`} />
                                    <TableCell className="whitespace-nowrap px-4 py-2.5 text-xs text-gray-500">
                                        {formatDt(log.created_at)}
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5 text-sm font-medium text-gray-900">
                                        {log.username_attempted || <span className="italic text-xs text-gray-400">-</span>}
                                    </TableCell>
                                    <TableCell className="max-w-56 truncate px-4 py-2.5 text-xs text-gray-600" title={log.failure_reason ?? ''}>
                                        {log.failure_reason || <span className="text-gray-400">-</span>}
                                    </TableCell>
                                    <TableCell className="px-4 py-2.5 text-xs text-gray-400">
                                        {log.ip_address || '-'}
                                    </TableCell>
                                    <TableCell className="max-w-64 truncate px-4 py-2.5 text-xs text-gray-400" title={log.user_agent ?? ''}>
                                        {log.user_agent || '-'}
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
