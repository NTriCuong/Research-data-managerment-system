"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { Bell } from "lucide-react";
import { useRouter } from "next/navigation";
import axiosInstance from "@/lib/axios/axios.instance";
import { API_ENDPOINT } from "@/lib/constants/api-endpoint";
import { listenForegroundMessage } from "@/lib/hooks/hooks";

interface Notification {
    id: string;
    title: string;
    message: string;
    notification_type: string;
    research_id: string | null;
    is_read: boolean;
    created_at: string;
}

interface NotificationBellProps {
    userId: string;
}

// Map notification_type → đường dẫn tương ứng theo role nhận
const NOTIFICATION_ROUTES: Record<string, string> = {
    PENDING_REVIEW: "/dashboard/review/researches",
    PENDING_APPROVAL: "/dashboard/approval/researches",
    REQUEST_REVISION: "/dashboard/data-entry/researches",
    APPROVAL: "/dashboard/data-entry/researches",
    REJECTED: "/dashboard/data-entry/researches",
};

type Tab = "all" | "unread";

export default function NotificationBell({ userId }: NotificationBellProps) {
    const router = useRouter();
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [open, setOpen] = useState(false);
    const [tab, setTab] = useState<Tab>("unread");
    const dropdownRef = useRef<HTMLDivElement>(null);

    const fetchNotifications = useCallback(async () => {
        try {
            const res = await axiosInstance.get(API_ENDPOINT.NOTIFICATION.GET);
            setNotifications(res.data);
        } catch (err) {
            console.error("Failed to fetch notifications", err);
        }
    }, []);

    // Đóng dropdown khi click ra ngoài
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
                setOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    useEffect(() => {
        if (!userId) return;
        fetchNotifications();
    }, [userId, fetchNotifications]);

    // Polling fallback mỗi 30 giây
    useEffect(() => {
        if (!userId) return;
        const interval = setInterval(fetchNotifications, 30_000);
        return () => clearInterval(interval);
    }, [userId, fetchNotifications]);

    // FCM foreground
    useEffect(() => {
        if (!userId) return;
        let unsubscribe: (() => void) | undefined;
        listenForegroundMessage((_payload) => {
            fetchNotifications();
        }).then((unsub) => {
            unsubscribe = unsub;
        });
        return () => { if (unsubscribe) unsubscribe(); };
    }, [userId, fetchNotifications]);

    const handleClickNotification = useCallback(async (n: Notification) => {
        // Đánh dấu đã đọc nếu chưa đọc
        if (!n.is_read) {
            try {
                await axiosInstance.patch(API_ENDPOINT.NOTIFICATION.MARK_READ(n.id));
                setNotifications((prev) =>
                    prev.map((item) => item.id === n.id ? { ...item, is_read: true } : item)
                );
            } catch (err) {
                console.error("Failed to mark as read", err);
            }
        }

        // Redirect đến trang detail nếu có research_id
        if (n.research_id) {
            const basePath = NOTIFICATION_ROUTES[n.notification_type];
            if (basePath) {
                router.push(`${basePath}/${n.research_id}`);
                setOpen(false);
            }
        }
    }, [router]);

    const unreadCount = notifications.filter((n) => !n.is_read).length;
    const displayed = tab === "unread"
        ? notifications.filter((n) => !n.is_read)
        : notifications;

    return (
        <div ref={dropdownRef} style={{ position: "relative" }}>
            {/* Bell icon */}
            <div
                onClick={() => setOpen((prev) => !prev)}
                style={{ cursor: "pointer", position: "relative", display: "inline-flex" }}
            >
                <Bell size={22} />
                {unreadCount > 0 && (
                    <span style={{
                        position: "absolute",
                        top: -6,
                        right: -6,
                        background: "#e53e3e",
                        color: "white",
                        borderRadius: "50%",
                        fontSize: 11,
                        fontWeight: 700,
                        minWidth: 18,
                        height: 18,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: "0 4px",
                    }}>
                        {unreadCount > 99 ? "99+" : unreadCount}
                    </span>
                )}
            </div>

            {/* Dropdown */}
            {open && (
                <div style={{
                    position: "absolute",
                    right: 0,
                    top: 34,
                    width: 340,
                    background: "white",
                    border: "1px solid #e2e8f0",
                    borderRadius: 10,
                    zIndex: 50,
                    boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
                    overflow: "hidden",
                }}>
                    {/* Header */}
                    <div style={{
                        padding: "12px 16px 0",
                        fontWeight: 700,
                        fontSize: 15,
                        color: "#1a202c",
                        borderBottom: "1px solid #e2e8f0",
                    }}>
                        <div style={{ marginBottom: 10 }}>Thông báo</div>

                        {/* Tabs */}
                        <div style={{ display: "flex", gap: 4 }}>
                            {(["unread", "all"] as Tab[]).map((t) => (
                                <button
                                    key={t}
                                    onClick={() => setTab(t)}
                                    style={{
                                        padding: "6px 14px",
                                        fontSize: 13,
                                        fontWeight: tab === t ? 600 : 400,
                                        color: tab === t ? "#1f3568" : "#718096",
                                        background: "transparent",
                                        border: "none",
                                        borderBottom: tab === t ? "2px solid #1f3568" : "2px solid transparent",
                                        cursor: "pointer",
                                        marginBottom: -1,
                                    }}
                                >
                                    {t === "unread" ? `Chưa đọc${unreadCount > 0 ? ` (${unreadCount})` : ""}` : "Tất cả"}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* List */}
                    <div style={{ maxHeight: 380, overflowY: "auto" }}>
                        {displayed.length === 0 ? (
                            <div style={{ padding: "24px 16px", color: "#a0aec0", textAlign: "center", fontSize: 14 }}>
                                {tab === "unread" ? "Không có thông báo chưa đọc" : "Không có thông báo"}
                            </div>
                        ) : (
                            displayed.map((n) => (
                                <div
                                    key={n.id}
                                    onClick={() => handleClickNotification(n)}
                                    style={{
                                        padding: "12px 16px",
                                        borderBottom: "1px solid #f7fafc",
                                        cursor: "pointer",
                                        background: n.is_read ? "white" : "#ebf4ff",
                                        display: "flex",
                                        gap: 10,
                                        alignItems: "flex-start",
                                        transition: "background 0.15s",
                                    }}
                                    onMouseEnter={(e) => {
                                        (e.currentTarget as HTMLDivElement).style.background = n.is_read ? "#f7fafc" : "#dbeafe";
                                    }}
                                    onMouseLeave={(e) => {
                                        (e.currentTarget as HTMLDivElement).style.background = n.is_read ? "white" : "#ebf4ff";
                                    }}
                                >
                                    {/* Dot chưa đọc */}
                                    <div style={{
                                        width: 8,
                                        height: 8,
                                        borderRadius: "50%",
                                        background: n.is_read ? "transparent" : "#3b82f6",
                                        flexShrink: 0,
                                        marginTop: 5,
                                    }} />

                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{
                                            fontWeight: n.is_read ? 400 : 600,
                                            fontSize: 13,
                                            color: "#2d3748",
                                            marginBottom: 2,
                                        }}>
                                            {n.title}
                                        </div>
                                        {n.message && (
                                            <div style={{
                                                color: "#718096",
                                                fontSize: 12,
                                                whiteSpace: "nowrap",
                                                overflow: "hidden",
                                                textOverflow: "ellipsis",
                                            }}>
                                                {n.message}
                                            </div>
                                        )}
                                        <div style={{ color: "#a0aec0", fontSize: 11, marginTop: 4 }}>
                                            {new Date(n.created_at).toLocaleString("vi-VN")}
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
