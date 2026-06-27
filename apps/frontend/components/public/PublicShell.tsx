"use client"

import type React from "react"
import Image from "next/image"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { LogIn, LayoutDashboard } from "lucide-react"

import { Button } from "@/components/ui/button"
import { useAppSelector } from "@/store/hooks"
import { getRoleHomePath } from "@/lib/auth/routes"

export function PublicShell({ children }: { children: React.ReactNode }) {
    const pathname = usePathname()
    const currentUser = useAppSelector((state) => state.auth.currentUser)
    const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated)
    const dashboardHref = currentUser ? getRoleHomePath(currentUser.role_name) : "/dashboard"

    return (
        <div className="flex min-h-screen flex-col bg-background">
            <header className="sticky top-0 z-30 border-b border-border bg-indigo-500 backdrop-blur">
                <div className="mx-auto flex h-28 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
                    <Link href="/" className="flex items-center gap-3">
                        <Image src="/logo-stu-white.svg" alt="STU" width={112} height={32} priority className="h-24 w-auto" />
                            <h1 className="scroll-m-20 text-center text-4xl font-extrabold tracking-tigh text-mist-50">
                            Cổng dữ liệu nghiên cứu khoa học
                            </h1>
                    </Link>
                    <nav className="flex items-center gap-1" aria-label="Điều hướng public">
                        <Button asChild variant={pathname === "/" ? "secondary" : "ghost"} size="lg">
                            <Link href="/">Trang chủ</Link>
                        </Button>
                        <Button asChild variant={pathname.startsWith("/researches") ? "secondary" : "ghost"} size="lg">
                            <Link href="/researches">Bộ lọc</Link>
                        </Button>
                        {isAuthenticated ? (
                            <Button asChild variant="outline" size="lg">
                                <Link href={dashboardHref}>
                                    <LayoutDashboard data-icon="inline-start" />
                                    Dashboard
                                </Link>
                            </Button>
                        ) : (
                            <Button asChild size="lg">
                                <Link href="/login">
                                    <LogIn data-icon="inline-start" />
                                    Đăng nhập
                                </Link>
                            </Button>
                        )}
                    </nav>
                </div>
            </header>
            <main className="flex-1">{children}</main>
            <footer className="border-t border-border bg-indigo-500">
                <div className="mx-auto grid w-full max-w-7xl gap-6 px-8 py-18 text-sm text-muted-foreground sm:px-6 md:grid-cols-4 lg:px-8">
                    <div>
                        <p className="font-semibold text-foreground">Phòng khoa học công nghệ</p>
                        <p className="mt-2 text-foreground">Trường Đại học Công nghệ Sài Gòn</p>
                    </div>
                    <div>
                        <p className="font-medium text-foreground">Liên hệ</p>
                        <p className="mt-2 text-foreground">Email: nckh@stu.edu.vn</p>
                        <p className="text-foreground">Điện thoại: (028) 3850 5520</p>
                    </div>
                    <div>
                        <p className="font-medium text-foreground">Địa chỉ</p>
                        <p className="mt-2 text-foreground">180 Cao Lỗ, Phường 4, Quận 8, TP. Hồ Chí Minh</p>
                    </div>
                    <div>
                        <Image src="/logo-stu-raw.svg" alt="STU" width={112} height={32} priority className="h-24 w-auto" />
                    </div>
                </div>
            </footer>
        </div>
    )
}
