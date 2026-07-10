import { logService } from "@/services/logs/log.service"
import { referenceService } from "@/services/reference/reference.service"
import {
    Activity,
    Plus,
    Pencil,
    Trash2,
    Check,
    X,
    Upload,
    Download,
    LogIn,
    LogOut,
} from "lucide-react"
import { LucideIcon } from "lucide-react"
import { useEffect, useState } from "react"

function formatDt(v: string) {
    return new Date(v).toLocaleString("vi-VN")
}

function relativeTime(v: string) {
    const diff = Date.now() - new Date(v).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return "Vừa xong"
    if (mins < 60) return `${mins} phút trước`
    const hours = Math.floor(mins / 60)
    if (hours < 24) return `${hours} giờ trước`
    const days = Math.floor(hours / 24)
    if (days < 7) return `${days} ngày trước`
    return new Date(v).toLocaleDateString("vi-VN")
}

interface ListAuditLogs {
    audit_id: string
    actor_user: string
    action_code: string
    created_at: string
}

// Map action code → { icon, màu, label tiếng Việt }
type ActionMeta = {
    icon: LucideIcon
    bg: string
    color: string
    label: string
}

function getActionMeta(code: string): ActionMeta {
    const upper = code.toUpperCase()
    if (upper.startsWith("CREATE") || upper.startsWith("ADD"))
        return { icon: Plus, bg: "bg-blue-50", color: "text-blue-600", label: "Tạo mới" }
    if (upper.startsWith("UPDATE") || upper.startsWith("EDIT"))
        return { icon: Pencil, bg: "bg-amber-50", color: "text-amber-600", label: "Cập nhật" }
    if (upper.startsWith("DELETE") || upper.startsWith("REMOVE"))
        return { icon: Trash2, bg: "bg-red-50", color: "text-red-600", label: "Xóa" }
    if (upper.startsWith("APPROVE"))
        return { icon: Check, bg: "bg-green-50", color: "text-green-600", label: "Phê duyệt" }
    if (upper.startsWith("REJECT"))
        return { icon: X, bg: "bg-red-50", color: "text-red-600", label: "Từ chối" }
    if (upper.startsWith("UPLOAD"))
        return { icon: Upload, bg: "bg-violet-50", color: "text-violet-600", label: "Tải lên" }
    if (upper.startsWith("DOWNLOAD"))
        return { icon: Download, bg: "bg-violet-50", color: "text-violet-600", label: "Tải xuống" }
    if (upper.startsWith("LOGIN"))
        return { icon: LogIn, bg: "bg-blue-50", color: "text-blue-600", label: "Đăng nhập" }
    if (upper.startsWith("LOGOUT"))
        return { icon: LogOut, bg: "bg-gray-50", color: "text-gray-600", label: "Đăng xuất" }
    return { icon: Activity, bg: "bg-gray-50", color: "text-gray-600", label: "Hành động" }
}

function RecentAuditLogs() {
    const [listAuditLogs, setListAuditLogs] = useState<ListAuditLogs[]>([])

    const fetch = async () => {
        const res = await logService.listAuditLogs({ limit: 8, offset: 0 })

        const userIds = Array.from(
            new Set(
                res
                    .map((log) => log.actor_user_id)
                    .filter((id): id is string => !!id)
            )
        )

        const userResults = await Promise.allSettled(
            userIds.map((id) => referenceService.getUserDetail(id))
        )

        const userNameMap = new Map<string, string>()
        userResults.forEach((result, idx) => {
            if (result.status === "fulfilled") {
                const user = result.value
                userNameMap.set(userIds[idx], user.full_name || user.username)
            }
        })

        const converted: ListAuditLogs[] = res.map((log) => ({
            audit_id: log.audit_id,
            actor_user: log.actor_user_id
                ? userNameMap.get(log.actor_user_id) ?? "Không xác định"
                : "Hệ thống",
            action_code: log.action_code,
            created_at: log.created_at,
        }))

        setListAuditLogs(converted)
    }

    useEffect(() => {
        fetch()
    }, [])

    return (
        <div className="rounded-2xl border border-gray-200 bg-white p-6">
            {/* Header */}
            <div className="mb-5 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
                        <Activity className="h-4 w-4 text-blue-600" />
                    </div>
                    <div>
                        <h3 className="text-[15px] font-semibold text-gray-900">
                            Hoạt động hệ thống
                        </h3>
                        <p className="text-xs text-gray-500">
                            {listAuditLogs.length} thao tác gần nhất
                        </p>
                    </div>
                </div>
            </div>

            {/* List */}
            <div className="space-y-1">
                {listAuditLogs.map((item) => {
                    const meta = getActionMeta(item.action_code)
                    const Icon = meta.icon
                    return (
                        <div
                            key={item.audit_id}
                            className="flex items-center gap-3 rounded-lg px-2 py-2 transition-colors hover:bg-gray-50"
                        >
                            {/* Action icon */}
                            <div
                                className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${meta.bg}`}
                            >
                                <Icon className={`h-4 w-4 ${meta.color}`} />
                            </div>

                            {/* Content */}
                            <div className="min-w-0 flex-1">
                                <div className="flex items-baseline justify-between gap-2">
                                    <p className="truncate text-sm text-gray-900">
                                        <span className="font-medium">
                                            {item.actor_user}
                                        </span>
                                        <span className="text-gray-500">
                                            {" "}· {meta.label}
                                        </span>
                                    </p>
                                    <span
                                        className="shrink-0 text-xs text-gray-400 tabular-nums"
                                        title={formatDt(item.created_at)}
                                    >
                                        {relativeTime(item.created_at)}
                                    </span>
                                </div>
                                <code className="mt-0.5 inline-block rounded bg-gray-100 px-1.5 py-0.5 font-mono text-[10px] text-gray-600">
                                    {item.action_code}
                                </code>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

export default RecentAuditLogs