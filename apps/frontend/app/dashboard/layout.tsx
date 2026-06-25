"use client";

import FirebaseInitializer from "@/components/filebase/FirebaseInitializer";
import NotificationButton from "@/components/filebase/NotificationButton";
import Header from "@/components/header/Header";
import Navbar, { type NavbarItem } from "@/components/navbar/Navbar";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useAppSelector } from "@/lib/hooks/hooks";
import { selectCurrentUser } from "@/store/slice/auth.slice";
import { CheckCheck, ClipboardList, FilePlus2, FileText, Users } from "lucide-react";

// menu data entry
const items_data_entry = [
    { label: "Researches", href: "/dashboard/data-entry/researches", icon: FileText },
    { label: "New Entry", href: "/dashboard/data-entry/new-entry", icon: FilePlus2 },
];
// menu reviewer
const items_reviewer = [
    { label: "Researches", href: "/dashboard/review/researches", icon: ClipboardList },
];
// menu approver
const items_approver = [
    { label: "Researches", href: "/dashboard/approval/researches", icon: CheckCheck },
];
// menu super admin
const items_super_admin = [
    { label: "Users", href: "/dashboard/superadmin/users", icon: Users },
];

// map role_name (đúng tên trả về từ backend) sang menu navbar tương ứng
const ROLE_NAVBAR_ITEMS: Record<string, NavbarItem[]> = {
    "Data Entry User": items_data_entry,
    "Metadata Reviewer": items_reviewer,
    "Metadata Approver": items_approver,
    "Super Administrator": items_super_admin,
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const currentUser = useAppSelector(selectCurrentUser);
    const items = currentUser ? ROLE_NAVBAR_ITEMS[currentUser.role_name] ?? [] : [];

    return (
        <ProtectedRoute>
            <FirebaseInitializer />
            <NotificationButton />
            <div className="flex h-screen flex-col">
                <div className="flex">
                    <div className="flex h-12 w-60 shrink-0 items-center bg-[#1f3568] px-4">
                        <span className="text-sm font-semibold text-white">RDMS</span>
                    </div>
                    <div className="flex-1">
                        <Header />
                    </div>
                </div>
                <div className="flex flex-1 overflow-hidden">
                    <Navbar items={items} />
                    <main className="flex-1 overflow-y-auto">{children}</main>
                </div>
            </div>
        </ProtectedRoute>
    );
}
