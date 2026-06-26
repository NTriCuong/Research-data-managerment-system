'use client'

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { User } from "lucide-react";
import { type CurrentUser } from "@/store/slice/auth.slice";
import { useAppDispatch } from "@/lib/hooks/hooks";
import { authService } from "@/services/auth/auth.service";
import { SidebarTrigger } from "@/components/ui/sidebar";
import NotificationBell from "../bell/NotificationBell";

interface AuthHeaderProps {
    currentUser: CurrentUser;
}

export default function AuthHeader({ currentUser }: AuthHeaderProps) {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);
    const dispatch = useAppDispatch();
    const router = useRouter();

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsMenuOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleLogout = async () => {
        await authService.logout(dispatch);
        router.replace("/login");
    };

    return (
        <header className="relative flex h-12 shrink-0 items-center justify-between border-b border-[#dcdcdc] bg-[#f7f7f7] pl-2 pr-10">
            <SidebarTrigger />
            <div className="flex items-center gap-7">
                <NotificationBell userId={currentUser.user_id} />

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
            </div>
        </header>
    );
}
