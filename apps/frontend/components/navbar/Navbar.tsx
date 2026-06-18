"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export interface NavbarItem {
    label: string;
    href: string;
}

interface NavbarProps {
    items: NavbarItem[];
}

export default function Navbar({ items }: NavbarProps) {
    const pathname = usePathname();

    return (
        <nav className="flex h-full w-1/6 shrink-0 flex-col bg-[#1f3568]">
            {items.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);

                return (
                    <Link
                        key={item.href}
                        href={item.href}
                        className={`px-6 py-3 text-sm font-medium transition ${isActive ? "bg-white/10 text-white" : "text-white/70 hover:bg-white/5 hover:text-white"
                            }`}
                    >
                        {item.label}
                    </Link>
                );
            })}
        </nav>
    );
}
