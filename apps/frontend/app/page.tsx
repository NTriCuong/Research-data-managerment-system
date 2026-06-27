"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowRight, BookOpen } from "lucide-react"

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
                <div className="mx-auto flex w-full max-w-7xl justify-center px-4 py-24 sm:px-6 lg:px-8">
                    <div className="w-full max-w-3xl text-center">
                        <div className="mx-auto mt-6 rounded-lg border border-border bg-background/95 p-2 shadow-sm backdrop-blur">
                            <PublicSearchForm />
                        </div>
                    </div>
                </div>
            </section>

            <section className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8 bg-accent-foreground/5">
                <div className="mb-4 flex items-center justify-between gap-3">
                    <div>
                        <h2 className="text-xl font-semibold text-foreground">Bài nghiên cứu mới nhất</h2>
                    </div>
                    <Button asChild variant="ghost" size="sm">
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
