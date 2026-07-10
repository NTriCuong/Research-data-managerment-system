import { LoginLog, logService } from "@/services/logs/log.service"
import { LogIn } from "lucide-react"
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

function initials(name: string) {
    return name.slice(0, 2).toUpperCase()
}

function RecentLoginLogs() {
    const [listLoginLogs, setListLoginLogs] = useState<LoginLog[]>([])

    const fetch = async () => {
        const res = await logService.listLoginLogs({ limit: 8, offset: 0 })
        setListLoginLogs(res)
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
                        <LogIn className="h-4 w-4 text-blue-600" />
                    </div>
                    <div>
                        <h3 className="text-[15px] font-semibold text-gray-900">
                            Hoạt động đăng nhập
                        </h3>
                        <p className="text-xs text-gray-500">
                            {listLoginLogs.length} lượt gần nhất
                        </p>
                    </div>
                </div>
            </div>

            {/* List */}
            <div className="space-y-1">
                {listLoginLogs.map((item) => {
                    const isSuccess = item.login_result === "success"
                    const username = item.username_attempted || "unknown"
                    return (
                        <div
                            key={item.login_log_id}
                            className="flex items-center gap-3 rounded-lg px-2 py-2 transition-colors hover:bg-gray-50"
                        >
                            {/* Avatar with status ring */}
                            <div className="relative shrink-0">
                                <div
                                    className={`flex h-9 w-9 items-center justify-center rounded-full text-xs font-semibold ring-2 ${isSuccess
                                        ? "bg-green-50 text-green-700 ring-green-200"
                                        : "bg-red-50 text-red-700 ring-red-200"
                                        }`}
                                >
                                    {initials(username)}
                                </div>
                                <span
                                    className={`absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full ring-2 ring-white ${isSuccess ? "bg-green-500" : "bg-red-500"
                                        }`}
                                />
                            </div>

                            {/* Content */}
                            <div className="min-w-0 flex-1">
                                <div className="flex items-baseline justify-between gap-2">
                                    <p className="truncate text-sm font-medium text-gray-900">
                                        {username}
                                    </p>
                                    <span
                                        className="shrink-0 text-xs text-gray-400 tabular-nums"
                                        title={formatDt(item.created_at)}
                                    >
                                        {relativeTime(item.created_at)}
                                    </span>
                                </div>
                                <p
                                    className={`truncate text-xs ${isSuccess
                                        ? "text-gray-500"
                                        : "text-red-600"
                                        }`}
                                >
                                    {isSuccess
                                        ? "Đăng nhập thành công"
                                        : "Đăng nhập thất bại"}
                                </p>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

export default RecentLoginLogs