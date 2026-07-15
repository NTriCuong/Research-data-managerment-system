"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowRight } from "lucide-react"

import { PublicShell } from "@/components/public/PublicShell"
import { PublicSearchForm } from "@/components/public/PublicSearchForm"
import { ResearchCard } from "@/components/public/ResearchCard"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { clientEnv } from "@/lib/env/client.env"
import {
    publicSearchService,
    type PublicResearchItem,
} from "@/services/public-search/public-search.service"


export default function HomePage() {
    const [items, setItems] = useState<PublicResearchItem[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")

    useEffect(() => {
        publicSearchService
            .listPublicResearches({ limit: 6, offset: 0 })
            .then((data) => setItems(data.items))
            .catch(() => setError("Không thể tải danh sách bài nghiên cứu public."))
            .finally(() => setLoading(false))
    }, [])

    const bannerUrl = clientEnv.NEXT_PUBLIC_PUBLIC_HOME_BANNER_URL

    return (
        <PublicShell>
            <section
                className="border-b border-border bg-muted/25 bg-cover bg-center"
                style={
                    bannerUrl
                        ? {
                            backgroundImage: `url("${bannerUrl}")`,
                        }
                        : undefined
                }
            >
                <div className="mx-auto flex w-full max-w-7xl justify-center px-4 py-70 sm:px-6 lg:px-8">
                </div>
            </section>
            <section className="border-b-2 border-border bg-muted/25">
                <div className="flex w-full justify-center px-4 py-20 sm:px-6 lg:px-8">
                    <div className="w-full max-w-3xl text-center">  
                        <div className="mx-auto mt-6 rounded-lg border-4 border-blue-400 bg-background/95 p-4 shadow-sm backdrop-blur">
                            <PublicSearchForm />
                        </div>
                    </div>
                </div>
            </section>
            <section className="border-b border-border bg-background">
                <div className="mx-auto w-full max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
                    <div className="mx-auto max-w-5xl text-base leading-8 text-muted-foreground sm:text-lg">
                        <div className="mb-8 text-center">
                            <h2 className="text-3xl font-bold tracking-tight text-primary sm:text-4xl">
                                Quy định
                            </h2>
                            <div className="mx-auto mt-4 h-1 w-16 rounded-full bg-primary/20" />
                        </div>

                        <p>
                            Các bộ dữ liệu, đề tài Báo cáo khoa học... của Trường Đại học công nghệ Sài Gòn được xây dựng nhằm hỗ trợ cho hoạt động giảng dạy và nghiên cứu của Nhà trường.
                        </p>
                        <p className="mt-4">
                            Trong quá trình phục vụ, người sử dụng được yêu cầu phải tuân thủ <strong className="font-semibold text-foreground">Luật Sở hữu Trí tuệ Việt Nam</strong> và <strong className="font-semibold text-foreground">Quy chế Quản trị tài sản trí tuệ Trường Đại học công nghệ Sài Gòn</strong>. Đồng thời, các chủ tài khoản phải tuân thủ một số quy định sau:
                        </p>

                        <ol className="mt-5 list-decimal space-y-1 pl-7 marker:text-foreground">
                            <li>Chỉ sử dụng tài liệu cho mục đích giảng dạy, học tập và nghiên cứu;</li>
                            <li>Khi bạn đọc được cung cấp tài khoản, vui lòng không tiết lộ hoặc chuyển giao tài khoản cho người khác sử dụng;</li>
                            <li>Không được sử dụng bất kỳ hình thức và công cụ tin học - công nghệ nào để sao chụp, tải dữ liệu một cách có hệ thống;</li>
                            <li>
                                Khi vi phạm các điều trên:
                                <ul className="mt-1 list-none space-y-1 pl-1">
                                    <li>- Thu hồi quyền truy cập;</li>
                                    <li>- Chịu trách nhiệm trước pháp luật nếu có;</li>
                                </ul>
                            </li>
                            <li>
                                <span>Điện thoại: (84.8) 3850 5520 - Ext: 206</span>
                                <br />
                                <span>
                                    Email:{" "}
                                    <a className="text-primary underline underline-offset-4 hover:text-primary/80" href="mailto:thuvien@hcmus.edu.vn">
                                        qlkh@stu.edu.vn
                                    </a>
                                </span>
                            </li>
                        </ol>
                    </div>
                </div>
            </section>
            <section className="border-b-2 border-border bg-blue-300">
                <div className="flex w-full justify-center px-4 py-7 sm:px-6 lg:px-8">
                    <h2 className="text-2xl font-semibold text-foreground">Dữ liệu mới nhất</h2>
                </div>
            </section>
            <section className="mx-auto w-full px-4 py-8 sm:px-6 lg:px-8">
                <div className="mb-4 flex items-center justify-end gap-3">
                    <Button asChild variant="ghost" size="lg">  
                        <Link href="/researches">
                            Xem tất cả
                            <ArrowRight data-icon="inline-end" />
                        </Link>
                    </Button>
                </div>

                {loading ? (
                    <div className="grid gap-4 lg:grid-cols-2" aria-busy="true">
                        {Array.from({ length: 6 }).map((_, index) => (
                            <Skeleton key={index} className="h-44 rounded-lg" />
                        ))}
                    </div>
                ) : error ? (
                    <div role="status" className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
                        {error}
                    </div>
                ) : items.length === 0 ? (
                    <div role="status" className="rounded-lg border border-border p-8 text-center text-sm text-muted-foreground">
                        Chưa có bài nghiên cứu nào được công bố.
                    </div>
                ) : (
                    <div className="grid gap-4 lg:grid-cols-2">
                        {items.map((research) => (
                            <ResearchCard key={research.research_id} research={research} />
                        ))}
                    </div>
                )}
            </section>
        </PublicShell>
    )
}
