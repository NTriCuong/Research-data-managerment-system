"use client"

import type React from "react"
import Image from "next/image"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { LogIn, LayoutDashboard } from "lucide-react"

import { Button } from "@/components/ui/button"
import { useAppSelector } from "@/lib/hooks/hooks"
import { getRoleHomePath } from "@/lib/auth/routes"
import { selectCurrentUser, selectIsAuthenticated } from "@/store/slice/auth.slice"

export function PublicShell({ children }: { children: React.ReactNode }) {
    const pathname = usePathname()
    const currentUser = useAppSelector(selectCurrentUser)
    const isAuthenticated = useAppSelector(selectIsAuthenticated)
    const dashboardHref = currentUser ? getRoleHomePath(currentUser.role_name) : "/dashboard"

    return (
        <div className="flex min-h-screen flex-col bg-background">
            <header className="sticky top-0 z-30 border-b border-border bg-blue-400 backdrop-blur">
                <div className="border-b border-gray-100 bg-white text-xs md:text-sm text-muted-foreground">
                    <div className="mx-auto flex h-10 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
                        <div className="flex gap-4">
                            <Link href="/lien-he" className="hover:text-foreground transition-colors">Liên hệ</Link>
                            <Link href="/quy-dinh" className="hover:text-foreground transition-colors">Quy định</Link>
                            <Link href="/huong-dan" className="hover:text-foreground transition-colors">Hướng dẫn</Link>
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="text-gray-300">|</span>
                            <button className="hover:text-foreground transition-colors">EN</button>
                            <button className="font-semibold text-foreground">VIE</button>
                        </div>
                    </div>
                </div>
                <div className="mx-auto flex h-24 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
                    <Link href="/" className="flex items-center gap-3">
                        <Image src="/logo-stu-white.svg" alt="STU" width={112} height={32} priority className="h-20 w-auto" />  
                    </Link>
                    <nav className="flex items-center gap-1" aria-label="Điều hướng public">
                        <Button asChild variant={pathname === "/" ? "secondary" : "ghost"} size="lg">
                            <Link href="/">Trang chủ</Link>
                        </Button>
                        <Button asChild variant={pathname.startsWith("/gioi-thieu") ? "secondary" : "ghost"} size="lg">
                            <Link href="/gioi-thieu">Giới thiệu</Link>
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
            <footer className="border-t border-border bg-blue-400">
                <div className="mx-auto grid w-full max-w-7xl gap-6 px-8 py-18 text-sm text-muted-foreground sm:px-6 md:grid-cols-4 lg:px-8">
                    <div>
                        <p className="font-semibold text-amber-50">Phòng khoa học công nghệ</p>
                        <p className="mt-2 text-amber-50">Trường Đại học Công nghệ Sài Gòn</p>
                    </div>
                    <div>
                        <p className="font-medium text-amber-50">Liên hệ</p>
                        <p className="mt-2 text-amber-50">Email: qlkh@stu.edu.vn</p>
                        <p className="text-amber-50">Điện thoại: (84.8) 3850 5520 - Ext: 206</p>
                    </div>
                    <div>
                        <p className="font-medium text-amber-50">Địa chỉ</p>
                        <p className="mt-2 text-amber-50">180 Cao Lỗ, Phường 4, Quận 8, TP. Hồ Chí Minh</p>
                        <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3919.9544104264664!2d106.67525180913164!3d10.73799718936426!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31752f62a90e5dbd%3A0x674d5126513db295!2zVHLGsOG7nW5nIMSQ4bqhaSBo4buNYyBDw7RuZyBuZ2jhu4cgU8OgaSBHw7Ju!5e0!3m2!1svi!2s!4v1783740818310!5m2!1svi!2s" className="mt-2 h-28 w-full border border-gray-300" ></iframe>
                    </div>
                    <div>
                        <Image src="/logo-stu-raw.svg" alt="STU" width={112} height={32} priority className="ml-30 h-24 w-auto" />
                    </div>
                </div>
            </footer>
            <footer className="bg-blue-500">
                <div className="mx-auto flex min-h-40 w-full max-w-7xl flex-col items-center justify-between gap-8 px-4 py-10 sm:px-6 md:flex-row lg:px-8">
                    <p className="max-w-2xl text-center text-amber-50 text-base font-medium leading-8 md:text-left">
                        <strong>© 2026</strong> Bản quyền thuộc Khoa công nghệ thông tin Trường Đại học Công nghệ Sài Gòn. <br/> Cung cấp bởi <strong>Trường Đại học Công nghệ Sài Gòn.</strong>
                    </p>
                    <div className="flex items-center gap-7 text-white/90" aria-label="Mạng xã hội">
                        <a href="https://www.facebook.com/" target="_blank" rel="noreferrer" aria-label="Facebook" className="transition hover:text-white hover:scale-110">
                            <Image src="/Facebook.svg" alt="Facebook" width={112} height={32} className="size-9  fill-current" />
                        </a>
                        <a href="https://www.instagram.com/" target="_blank" rel="noreferrer" aria-label="Instagram" className="transition hover:text-white hover:scale-110">
                            <Image src="/Instagram.svg" alt="Instagram" width={112} height={32} className="size-12 fill-current"  />
                        </a>
                        <a href="https://www.youtube.com/" target="_blank" rel="noreferrer" aria-label="YouTube" className="transition hover:text-white hover:scale-110">
                            <Image src="/Youtube.svg" alt="YouTube" width={112} height={32} className="size-12 fill-current"  />
                        </a>
                    </div>
                </div>
            </footer>
        </div>
    )
}
