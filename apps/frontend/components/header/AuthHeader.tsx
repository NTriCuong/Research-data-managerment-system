'use client'

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Bell, User } from "lucide-react";
import { selectAccessToken, type CurrentUser } from "@/store/slice/auth.slice";
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { authService } from "@/services/auth/auth.service";
import { notificationService, type AppNotification } from "@/services/notifications/notification.service";

interface AuthHeaderProps {
    currentUser: CurrentUser;
}

export default function AuthHeader({ currentUser }: AuthHeaderProps) {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isNotificationOpen, setIsNotificationOpen] = useState(false);
    const [notifications, setNotifications] = useState<AppNotification[]>([]);
    const menuRef = useRef<HTMLDivElement>(null);
    const notificationRef = useRef<HTMLDivElement>(null);
    const dispatch = useAppDispatch();
    const accessToken = useAppSelector(selectAccessToken);
    const router = useRouter();
    const unreadCount = notifications.filter((item) => !item.read_at).length;

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsMenuOpen(false);
            }
            if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
                setIsNotificationOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    useEffect(() => {
        if (!accessToken) return;

        let isMounted = true;
        notificationService.list()
            .then((data) => {
                if (isMounted) setNotifications(data);
            })
            .catch(() => undefined);

        return () => {
            isMounted = false;
        };
    }, [accessToken]);

    const handleLogout = async () => {
        await authService.logout(dispatch);
        router.replace("/login");
    };

    const handleNotificationClick = async (notification: AppNotification) => {
        if (!notification.read_at) {
            const updated = await notificationService.markRead(notification.notification_id);
            setNotifications((current) =>
                current.map((item) =>
                    item.notification_id === updated.notification_id ? updated : item
                )
            );
        }
        setIsNotificationOpen(false);
        if (notification.target_url) {
            router.push(notification.target_url);
        }
    };

    return (
        <header className="relative flex h-12 items-center justify-end gap-7 border-b border-[#dcdcdc] bg-[#f7f7f7] pr-12.5">
            <div ref={notificationRef} className="relative">
                <button
                    type="button"
                    aria-label="Notifications"
                    onClick={() => setIsNotificationOpen((open) => !open)}
                    className="relative flex cursor-pointer items-center text-[#5f6f8c] transition hover:text-[#1f3568]"
                >
                    <Bell size={22} />
                    {unreadCount > 0 && (
                        <span className="absolute -right-2 -top-2 flex min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-semibold leading-4 text-white">
                            {unreadCount > 9 ? "9+" : unreadCount}
                        </span>
                    )}
                </button>

                {isNotificationOpen && (
                    <div className="absolute top-full right-0 z-20 mt-2 w-80 max-w-[calc(100vw-2rem)] rounded-lg border border-gray-200 bg-white py-2 shadow-lg">
                        <div className="border-b border-gray-100 px-4 py-2">
                            <p className="text-sm font-semibold text-gray-800">Thông báo</p>
                        </div>
                        <div className="max-h-96 overflow-y-auto">
                            {notifications.length === 0 ? (
                                <p className="px-4 py-6 text-center text-sm text-gray-500">Chưa có thông báo</p>
                            ) : (
                                notifications.map((notification) => (
                                    <button
                                        key={notification.notification_id}
                                        type="button"
                                        onClick={() => handleNotificationClick(notification)}
                                        className="w-full cursor-pointer border-b border-gray-50 px-4 py-3 text-left transition last:border-b-0 hover:bg-gray-50"
                                    >
                                        <div className="flex items-start gap-2">
                                            {!notification.read_at && (
                                                <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[#1f3568]" />
                                            )}
                                            <div className="min-w-0 flex-1">
                                                <p className="truncate text-sm font-semibold text-gray-800">
                                                    {notification.title}
                                                </p>
                                                <p className="mt-1 line-clamp-2 text-xs text-gray-600">
                                                    {notification.message}
                                                </p>
                                            </div>
                                        </div>
                                    </button>
                                ))
                            )}
                        </div>
                    </div>
                )}
            </div>

            <div ref={menuRef} className="relative">
                <button
                    type="button"
                    aria-label="Account"
                    onClick={() => setIsMenuOpen((open) => !open)}
                    className="flex cursor-pointer items-center text-[#5f6f8c] transition hover:text-[#1f3568]"
                >
                    <User size={22} />
                </button>

                {isMenuOpen && (
                    <div className="absolute top-full right-0 z-10 mt-2 w-64 rounded-lg border border-gray-200 bg-white py-3 shadow-lg">
                        <div className="border-b border-gray-100 px-4 pb-3">
                            <p className="truncate text-sm font-semibold text-gray-800">{currentUser.full_name}</p>
                            <p className="truncate text-xs text-gray-500">{currentUser.email}</p>
                            <p className="mt-1 inline-block rounded-full bg-[#1f3568]/10 px-2 py-0.5 text-xs font-medium text-[#1f3568]">
                                {currentUser.role_name}
                            </p>
                        </div>
                        <button
                            type="button"
                            onClick={handleLogout}
                            className="mt-2 w-full cursor-pointer px-4 py-2 text-left text-sm text-red-500 transition hover:bg-red-50"
                        >
                            Đăng xuất
                        </button>
                    </div>
                )}
            </div>
        </header>
    );
}
