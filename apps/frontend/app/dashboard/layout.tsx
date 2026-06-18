"use client";

import Header from "@/components/header/Header";
import Navbar from "@/components/navbar/Navbar";
import ProtectedRoute from "@/components/ProtectedRoute";

const items = [
    { label: "Researches", href: "/dashboard/data-entry/researches" },
    { label: "New Entry", href: "/dashboard/data-entry/new-entry" },
    { label: "Update Metadata", href: "/dashboard/data-entry/update-metadata" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
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
