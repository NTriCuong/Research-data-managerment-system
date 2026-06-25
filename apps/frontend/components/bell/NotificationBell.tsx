"use client";

import { useEffect, useState } from "react";
import axios from "axios";

export default function NotificationBell() {
    const [notifications, setNotifications] = useState([]);
    const [open, setOpen] = useState(false);

    const fetchNotifications = async () => {
        const res = await axios.get("http://localhost:8000/api/v1/notifications");
        setNotifications(res.data);
    };

    useEffect(() => {
        fetchNotifications();
    }, []);

    const unreadCount = notifications.filter((n: any) => !n.is_read).length;

    return (
        <div style={{ position: "relative", cursor: "pointer" }}>
            {/* Chuông */}
            <div onClick={() => setOpen(!open)} style={{ fontSize: 24 }}>
                🔔
                {unreadCount > 0 && (
                    <span style={{
                        position: "absolute",
                        top: -5,
                        right: -5,
                        background: "red",
                        color: "white",
                        borderRadius: "50%",
                        fontSize: 12,
                        padding: "2px 6px"
                    }}>
                        {unreadCount}
                    </span>
                )}
            </div>

            {/* Dropdown */}
            {open && (
                <div style={{
                    position: "absolute",
                    right: 0,
                    top: 30,
                    width: 300,
                    background: "white",
                    border: "1px solid #ccc",
                    padding: 10
                }}>
                    {notifications.map((n: any) => (
                        <div key={n.id} style={{ padding: 5 }}>
                            {n.title}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}