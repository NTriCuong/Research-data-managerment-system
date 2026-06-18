"use client";

import Header from "@/components/header/Header";
import Navbar, { type NavbarItem } from "@/components/navbar/Navbar";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useAppSelector } from "@/store/hooks";
import { selectCurrentUser } from "@/store/slice/auth.slice";

// menu data entry
const items_data_entry = [
    { label: "Researches", href: "/dashboard/data-entry/researches" },
    { label: "New Entry", href: "/dashboard/data-entry/new-entry" },
];
// menu reviewer
const items_reviewer = [
    { label: "Researches", href: "/dashboard/review/researches" },
];

// map role_name (đúng tên trả về từ backend) sang menu navbar tương ứng
const ROLE_NAVBAR_ITEMS: Record<string, NavbarItem[]> = {
    "Data Entry User": items_data_entry,
    "Metadata Reviewer": items_reviewer,
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const currentUser = useAppSelector(selectCurrentUser);
    const items = currentUser ? ROLE_NAVBAR_ITEMS[currentUser.role_name] ?? [] : [];

    return (
        <ProtectedRoute>
            <div className="flex h-screen flex-col">
                <div className="flex">
                    <div className="h-12 w-1/6 shrink-0 bg-[#1f3568]" />
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
