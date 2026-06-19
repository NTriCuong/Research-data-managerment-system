"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { LucideIcon } from "lucide-react";

export interface NavbarItem {
    label: string;
    href: string;
    icon?: LucideIcon;
}

interface NavbarProps {
    items: NavbarItem[];
}

export default function Navbar({ items }: NavbarProps) {
    const pathname = usePathname();

    return (
        <nav className="flex h-full w-60 shrink-0 flex-col bg-[#1f3568]">
            <div className="flex flex-col gap-1 p-3">
                {items.map((item) => {
                    const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
                    const Icon = item.icon;

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${isActive ? "bg-white/15 text-white" : "text-white/70 hover:bg-white/5 hover:text-white"
                                }`}
                        >
                            {Icon && <Icon size={18} className={isActive ? "text-white" : "text-white/60"} />}
                            {item.label}
                        </Link>
                    );
                })}
            </div>
        </nav>
    );
}
