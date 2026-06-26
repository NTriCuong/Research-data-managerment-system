"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { Bell } from "lucide-react";
import { useRouter } from "next/navigation";
import axiosInstance from "@/lib/axios/axios.instance";
import { API_ENDPOINT } from "@/lib/constants/api-endpoint";

interface Notification {
    notification_id: string;
    event_type: string;
    title: string;
    message: string;
    target_url: string | null;
    read_at: string | null;
    created_at: string;
}

interface NotificationBellProps {
    userId: string;
}

type Tab = "all" | "unread";

export default function NotificationBell({ userId }: NotificationBellProps) {
    const router = useRouter();
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [open, setOpen] = useState(false);
    const [tab, setTab] = useState<Tab>("unread");
    const dropdownRef = useRef<HTMLDivElement>(null);

    const fetchNotifications = useCallback(async () => {
        try {
            const res = await axiosInstance.get(API_ENDPOINT.NOTIFICATIONS.LIST);
            setNotifications(res.data);
        } catch {
            // ignore
        }
    }, []);

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
        window.addEventListener("fcm-message", fetchNotifications);
        return () => window.removeEventListener("fcm-message", fetchNotifications);
    }, [userId, fetchNotifications]);

    const handleClickNotification = useCallback(async (n: Notification) => {
        if (!n.read_at) {
            try {
                const res = await axiosInstance.post(
                    API_ENDPOINT.NOTIFICATIONS.MARK_READ(n.notification_id)
                );
                setNotifications((prev) =>
                    prev.map((item) =>
                        item.notification_id === n.notification_id ? res.data : item
                    )
                );
            } catch {
                // ignore
            }
        }

        setOpen(false);

        if (n.target_url) {
            router.push(n.target_url);
        }
    }, [router]);

    const unreadCount = notifications.filter((n) => !n.read_at).length;
    const displayed = tab === "unread"
        ? notifications.filter((n) => !n.read_at)
        : notifications;

    return (
        <div ref={dropdownRef} style={{ position: "relative" }}>
            <button
                type="button"
                aria-label="Notifications"
                onClick={() => setOpen((prev) => !prev)}
                style={{ cursor: "pointer", position: "relative", display: "inline-flex", background: "none", border: "none", padding: 0, color: "#5f6f8c" }}
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
            </button>

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
                    <div style={{
                        padding: "12px 16px 0",
                        fontWeight: 700,
                        fontSize: 15,
                        color: "#1a202c",
                        borderBottom: "1px solid #e2e8f0",
                    }}>
                        <div style={{ marginBottom: 10 }}>Thông báo</div>

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

                    <div style={{ maxHeight: 380, overflowY: "auto" }}>
                        {displayed.length === 0 ? (
                            <div style={{ padding: "24px 16px", color: "#a0aec0", textAlign: "center", fontSize: 14 }}>
                                {tab === "unread" ? "Không có thông báo chưa đọc" : "Không có thông báo"}
                            </div>
                        ) : (
                            displayed.map((n) => {
                                const isUnread = !n.read_at;
                                return (
                                    <div
                                        key={n.notification_id}
                                        onClick={() => handleClickNotification(n)}
                                        style={{
                                            padding: "12px 16px",
                                            borderBottom: "1px solid #f7fafc",
                                            cursor: "pointer",
                                            background: isUnread ? "#ebf4ff" : "white",
                                            display: "flex",
                                            gap: 10,
                                            alignItems: "flex-start",
                                            transition: "background 0.15s",
                                        }}
                                        onMouseEnter={(e) => {
                                            (e.currentTarget as HTMLDivElement).style.background = isUnread ? "#dbeafe" : "#f7fafc";
                                        }}
                                        onMouseLeave={(e) => {
                                            (e.currentTarget as HTMLDivElement).style.background = isUnread ? "#ebf4ff" : "white";
                                        }}
                                    >
                                        <div style={{
                                            width: 8,
                                            height: 8,
                                            borderRadius: "50%",
                                            background: isUnread ? "#3b82f6" : "transparent",
                                            flexShrink: 0,
                                            marginTop: 5,
                                        }} />

                                        <div style={{ flex: 1, minWidth: 0 }}>
                                            <div style={{
                                                fontWeight: isUnread ? 600 : 400,
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
                                );
                            })
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
