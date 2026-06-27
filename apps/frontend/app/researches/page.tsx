"use client"

import { Suspense, useEffect, useMemo, useState } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { SlidersHorizontal, RotateCcw } from "lucide-react"

import { PublicShell } from "@/components/public/PublicShell"
import { PublicSearchForm } from "@/components/public/PublicSearchForm"
import { ResearchCard } from "@/components/public/ResearchCard"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { RtlPagination } from "@/components/ui/rtl-pagination"
import {
    publicSearchService,
    type PublicLookup,
    type PublicResearchItem,
    type PublicResearchLookups,
} from "@/services/public-search/public-search.service"

const PAGE_SIZE = 12
const ALL = "all"

function getParam(searchParams: URLSearchParams, key: string) {
    return searchParams.get(key) || ""
}

function ResearchesContent() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const [items, setItems] = useState<PublicResearchItem[]>([])
    const [lookups, setLookups] = useState<PublicResearchLookups | null>(null)
    const [total, setTotal] = useState(0)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")

    const params = useMemo(() => new URLSearchParams(searchParams.toString()), [searchParams])
    const page = Math.max(1, Number(params.get("page") || "1"))
    const q = getParam(params, "q")

    useEffect(() => {
        publicSearchService
            .getPublicResearchLookups()
            .then(setLookups)
            .catch(() => setLookups({ output_types: [], departments: [], domains: [], keywords: [] }))
    }, [])

    useEffect(() => {
        Promise.resolve()
            .then(() => {
                setLoading(true)
                setError("")
                return publicSearchService.listPublicResearches({
                    q: getParam(params, "q") || undefined,
                    output_type_id: getParam(params, "output_type_id") || undefined,
                    department_id: getParam(params, "department_id") || undefined,
                    domain_id: getParam(params, "domain_id") || undefined,
                    keyword_id: getParam(params, "keyword_id") || undefined,
                    year: getParam(params, "year") || undefined,
                    limit: PAGE_SIZE,
                    offset: (page - 1) * PAGE_SIZE,
                })
            })
            .then((data) => {
                setItems(data.items)
                setTotal(data.total)
            })
            .catch(() => setError("Không thể tải danh sách bài nghiên cứu."))
            .finally(() => setLoading(false))
    }, [params, page])

    const updateParam = (key: string, value: string) => {
        const next = new URLSearchParams(searchParams.toString())
        if (!value || value === ALL) {
            next.delete(key)
        } else {
            next.set(key, value)
        }
        next.delete("page")
        router.push(`/researches${next.size ? `?${next.toString()}` : ""}`)
    }

    const updatePage = (nextPage: number) => {
        const next = new URLSearchParams(searchParams.toString())
        if (nextPage <= 1) {
            next.delete("page")
        } else {
            next.set("page", String(nextPage))
        }
        router.push(`/researches${next.size ? `?${next.toString()}` : ""}`)
    }

    const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

    return (
        <PublicShell>
            <section className="border-b border-border bg-muted/25">
                <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                    <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
                        <div>
                            <h1 className="text-2xl font-semibold text-foreground">Bộ lọc</h1>
                        </div>
                        <Button asChild variant="outline" size="sm">
                            <Link href="/researches">
                                <RotateCcw size={16} />
                                Đặt lại
                            </Link>
                        </Button>
                    </div>
                    <div className="mt-5">
                        <PublicSearchForm initialQuery={q} />
                    </div>
                </div>
            </section>

            <section className="mx-auto grid w-full max-w-7xl gap-5 px-4 py-6 sm:px-6 lg:grid-cols-[280px_1fr] lg:px-8 bg-accent-foreground/5">
                <aside className="h-fit rounded-lg border border-border bg-card p-4">
                    <div className="mb-4 flex items-center gap-2">
                        <SlidersHorizontal className="size-4" />
                        <h2 className="font-semibold text-foreground">Duyệt theo</h2>
                    </div>
                    <div className="grid gap-4">
                        <FilterSelect
                            label="Loại công bố"
                            value={getParam(params, "output_type_id")}
                            options={lookups?.output_types ?? []}
                            onChange={(value) => updateParam("output_type_id", value)}
                        />
                        <FilterSelect
                            label="Khoa/đơn vị"
                            value={getParam(params, "department_id")}
                            options={lookups?.departments ?? []}
                            onChange={(value) => updateParam("department_id", value)}
                        />
                        <FilterSelect
                            label="Lĩnh vực"
                            value={getParam(params, "domain_id")}
                            options={lookups?.domains ?? []}
                            onChange={(value) => updateParam("domain_id", value)}
                        />
                        <FilterSelect
                            label="Từ khóa"
                            value={getParam(params, "keyword_id")}
                            options={lookups?.keywords ?? []}
                            onChange={(value) => updateParam("keyword_id", value)}
                        />
                        <div className="grid gap-2">
                            <Label htmlFor="year-filter">Năm</Label>
                            <select
                                id="year-filter"
                                value={getParam(params, "year")}
                                onChange={(event) => updateParam("year", event.target.value)}
                                className="h-8 rounded-lg border border-input bg-background px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                            >
                                <option value="">Tất cả</option>
                                {Array.from({ length: 30 }).map((_, index) => {
                                    const year = new Date().getFullYear() - index
                                    return (
                                        <option key={year} value={year}>
                                            {year}
                                        </option>
                                    )
                                })}
                            </select>
                        </div>
                    </div>
                </aside>

                <div>
                    <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                        <p className="text-sm text-muted-foreground">
                            {loading ? "Đang tải..." : `${total} bài nghiên cứu phù hợp`}
                        </p>
                        <p className="text-sm text-muted-foreground">
                            Trang {page} / {totalPages}
                        </p>
                    </div>

                    {loading ? (
                        <div className="grid gap-4" aria-busy="true">
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
                            Không có kết quả phù hợp.
                        </div>
                    ) : (
                        <div className="grid gap-4">
                            {items.map((research) => (
                                <ResearchCard key={research.research_id} research={research} variant="row" />
                            ))}
                        </div>
                    )}

                    <RtlPagination page={page} totalPages={totalPages} onPageChange={updatePage} className="mt-6" />
                </div>
            </section>
        </PublicShell>
    )
}

function FilterSelect({
    label,
    value,
    options,
    onChange,
}: {
    label: string
    value: string
    options: PublicLookup[]
    onChange: (value: string) => void
}) {
    return (
        <div className="grid gap-2">
            <Label>{label}</Label>
            <Select value={value || ALL} onValueChange={onChange}>
                <SelectTrigger className="w-full">
                    <SelectValue placeholder="Tất cả" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value={ALL}>Tất cả</SelectItem>
                    {options.map((option) => (
                        <SelectItem key={option.id} value={option.id}>
                            {option.name}
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>
        </div>
    )
}

export default function ResearchesPage() {
    return (
        <Suspense fallback={<PublicShell><div className="mx-auto max-w-7xl px-4 py-8">Đang tải...</div></PublicShell>}>
            <ResearchesContent />
        </Suspense>
    )
}
