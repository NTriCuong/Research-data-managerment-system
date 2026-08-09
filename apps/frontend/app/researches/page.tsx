"use client"

import { Suspense, useEffect, useMemo, useState } from "react"
import { Filter, RotateCcw, X } from "lucide-react"
import { useRouter, useSearchParams } from "next/navigation"

import { PublicShell } from "@/components/public/PublicShell"
import {
    ResearchFilters,
    type ResearchFilterState,
} from "@/components/public/ResearchFilters"
import { PublicSearchForm } from "@/components/public/PublicSearchForm"
import { ResearchCard } from "@/components/public/ResearchCard"
import { Button } from "@/components/ui/button"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetFooter,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import { RtlPagination } from "@/components/ui/rtl-pagination"
import {
    publicSearchService,
    type PublicLookup,
    type PublicResearchItem,
    type PublicResearchLookups,
    type PublicResearchSort,
} from "@/services/public-search/public-search.service"

const PAGE_SIZE = 12
const FILTER_PARAM_KEYS = [
    "output_type_ids",
    "department_ids",
    "domain_ids",
    "keyword_ids",
    "author_ids",
    "year_from",
    "year_to",
    "has_files",
    "output_type_id",
    "department_id",
    "domain_id",
    "keyword_id",
    "year",
] as const

const SORT_OPTIONS: Array<{ value: PublicResearchSort; label: string }> = [
    { value: "relevance", label: "Phù hợp nhất" },
    { value: "newest", label: "Mới nhất" },
    { value: "oldest", label: "Cũ nhất" },
    { value: "most_viewed", label: "Truy cập nhiều nhất" },
    { value: "most_downloaded", label: "Tải nhiều nhất" },
    { value: "title_asc", label: "Tiêu đề A-Z" },
]

const EMPTY_FILTERS: ResearchFilterState = {
    outputTypeIds: [],
    departmentIds: [],
    domainIds: [],
    keywordIds: [],
    authorIds: [],
    yearFrom: "",
    yearTo: "",
    hasFiles: false,
}

function getParam(searchParams: URLSearchParams, key: string) {
    return searchParams.get(key) || ""
}

function getIds(searchParams: URLSearchParams, key: string, legacyKey?: string) {
    return Array.from(
        new Set([
            ...searchParams.getAll(key),
            ...(legacyKey && searchParams.get(legacyKey) ? [searchParams.get(legacyKey)!] : []),
        ])
    )
}

function readFilters(searchParams: URLSearchParams): ResearchFilterState {
    return {
        outputTypeIds: getIds(searchParams, "output_type_ids", "output_type_id"),
        departmentIds: getIds(searchParams, "department_ids", "department_id"),
        domainIds: getIds(searchParams, "domain_ids", "domain_id"),
        keywordIds: getIds(searchParams, "keyword_ids", "keyword_id"),
        authorIds: getIds(searchParams, "author_ids"),
        yearFrom: getParam(searchParams, "year_from") || getParam(searchParams, "year"),
        yearTo: getParam(searchParams, "year_to") || getParam(searchParams, "year"),
        hasFiles: getParam(searchParams, "has_files") === "true",
    }
}

function lookupName(options: PublicLookup[], id: string) {
    return options.find((option) => option.id === id)?.name ?? id
}

function ResearchesContent() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const [items, setItems] = useState<PublicResearchItem[]>([])
    const [lookups, setLookups] = useState<PublicResearchLookups | null>(null)
    const [total, setTotal] = useState(0)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")
    const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false)
    const [draftFilters, setDraftFilters] = useState<ResearchFilterState>(EMPTY_FILTERS)

    const params = useMemo(() => new URLSearchParams(searchParams.toString()), [searchParams])
    const filters = useMemo(() => readFilters(params), [params])
    const page = Math.max(1, Number(params.get("page") || "1"))
    const q = getParam(params, "q")
    const requestedSort = getParam(params, "sort") as PublicResearchSort
    const sort = SORT_OPTIONS.some((option) => option.value === requestedSort)
        ? requestedSort
        : q
            ? "relevance"
            : "newest"

    useEffect(() => {
        publicSearchService
            .getPublicResearchLookups()
            .then(setLookups)
            .catch(() => setLookups({
                output_types: [],
                departments: [],
                domains: [],
                keywords: [],
                authors: [],
                year_min: null,
                year_max: null,
            }))
    }, [])

    useEffect(() => {
        Promise.resolve()
            .then(() => {
                setLoading(true)
                setError("")
                return publicSearchService.listPublicResearches({
                    q: q || undefined,
                    output_type_ids: filters.outputTypeIds,
                    department_ids: filters.departmentIds,
                    domain_ids: filters.domainIds,
                    keyword_ids: filters.keywordIds,
                    author_ids: filters.authorIds,
                    year_from: filters.yearFrom || undefined,
                    year_to: filters.yearTo || undefined,
                    has_files: filters.hasFiles,
                    sort,
                    limit: PAGE_SIZE,
                    offset: (page - 1) * PAGE_SIZE,
                })
            })
            .then((data) => {
                setItems(data.items)
                setTotal(data.total)
            })
            .catch(() => setError("Không thể tải danh sách kết quả nghiên cứu."))
            .finally(() => setLoading(false))
    }, [filters, page, q, sort])

    const pushParams = (next: URLSearchParams) => {
        router.push(`/researches${next.size ? `?${next.toString()}` : ""}`)
    }

    const applyFilters = (nextFilters: ResearchFilterState) => {
        const next = new URLSearchParams(searchParams.toString())
        FILTER_PARAM_KEYS.forEach((key) => next.delete(key))

        nextFilters.outputTypeIds.forEach((id) => next.append("output_type_ids", id))
        nextFilters.departmentIds.forEach((id) => next.append("department_ids", id))
        nextFilters.domainIds.forEach((id) => next.append("domain_ids", id))
        nextFilters.keywordIds.forEach((id) => next.append("keyword_ids", id))
        nextFilters.authorIds.forEach((id) => next.append("author_ids", id))

        let yearFrom = nextFilters.yearFrom
        let yearTo = nextFilters.yearTo
        if (yearFrom && yearTo && Number(yearFrom) > Number(yearTo)) {
            ;[yearFrom, yearTo] = [yearTo, yearFrom]
        }
        if (yearFrom) next.set("year_from", yearFrom)
        if (yearTo) next.set("year_to", yearTo)
        if (nextFilters.hasFiles) next.set("has_files", "true")
        next.delete("page")
        pushParams(next)
    }

    const updatePage = (nextPage: number) => {
        const next = new URLSearchParams(searchParams.toString())
        if (nextPage <= 1) next.delete("page")
        else next.set("page", String(nextPage))
        pushParams(next)
    }

    const updateSort = (nextSort: PublicResearchSort) => {
        const next = new URLSearchParams(searchParams.toString())
        next.set("sort", nextSort)
        next.delete("page")
        pushParams(next)
    }

    const resetFilters = () => applyFilters(EMPTY_FILTERS)
    const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
    const activeFilterCount =
        filters.outputTypeIds.length +
        filters.departmentIds.length +
        filters.domainIds.length +
        filters.keywordIds.length +
        filters.authorIds.length +
        Number(Boolean(filters.yearFrom || filters.yearTo)) +
        Number(filters.hasFiles)

    const activeChips = [
        ...filters.outputTypeIds.map((id) => ({
            key: `output-${id}`,
            label: lookupName(lookups?.output_types ?? [], id),
            remove: () => applyFilters({ ...filters, outputTypeIds: filters.outputTypeIds.filter((value) => value !== id) }),
        })),
        ...filters.departmentIds.map((id) => ({
            key: `department-${id}`,
            label: lookupName(lookups?.departments ?? [], id),
            remove: () => applyFilters({ ...filters, departmentIds: filters.departmentIds.filter((value) => value !== id) }),
        })),
        ...filters.domainIds.map((id) => ({
            key: `domain-${id}`,
            label: lookupName(lookups?.domains ?? [], id),
            remove: () => applyFilters({ ...filters, domainIds: filters.domainIds.filter((value) => value !== id) }),
        })),
        ...filters.authorIds.map((id) => ({
            key: `author-${id}`,
            label: lookupName(lookups?.authors ?? [], id),
            remove: () => applyFilters({ ...filters, authorIds: filters.authorIds.filter((value) => value !== id) }),
        })),
        ...filters.keywordIds.map((id) => ({
            key: `keyword-${id}`,
            label: lookupName(lookups?.keywords ?? [], id),
            remove: () => applyFilters({ ...filters, keywordIds: filters.keywordIds.filter((value) => value !== id) }),
        })),
        ...(filters.yearFrom || filters.yearTo
            ? [{
                key: "years",
                label: filters.yearFrom && filters.yearTo
                    ? `${filters.yearFrom}–${filters.yearTo}`
                    : filters.yearFrom
                        ? `Từ ${filters.yearFrom}`
                        : `Đến ${filters.yearTo}`,
                remove: () => applyFilters({ ...filters, yearFrom: "", yearTo: "" }),
            }]
            : []),
        ...(filters.hasFiles
            ? [{
                key: "has-files",
                label: "Có tệp toàn văn",
                remove: () => applyFilters({ ...filters, hasFiles: false }),
            }]
            : []),
    ]

    return (
        <PublicShell>
            <section className="border-b border-border bg-muted/20">
                <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                    <div className="grid items-end gap-5 md:grid-cols-[minmax(0,1fr)_minmax(360px,0.9fr)]">
                        <div>
                            <h1 className="text-2xl font-semibold text-foreground sm:text-3xl">
                                Khám phá kết quả nghiên cứu
                            </h1>
                            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                Tìm theo tiêu đề, tác giả, mã định danh hoặc từ khóa.
                            </p>
                        </div>
                        <PublicSearchForm initialQuery={q} />
                    </div>
                </div>
            </section>

            <section className="mx-auto grid w-full max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[300px_minmax(0,1fr)] lg:px-8">
                <aside className="hidden h-fit border-r border-border pr-5 lg:block">
                    <div className="mb-5 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Filter className="size-4" aria-hidden="true" />
                            <h2 className="font-semibold text-foreground">Bộ lọc</h2>
                        </div>
                        {activeFilterCount > 0 && (
                            <Button type="button" variant="ghost" size="icon-sm" onClick={resetFilters} title="Đặt lại bộ lọc">
                                <RotateCcw className="size-4" />
                                <span className="sr-only">Đặt lại bộ lọc</span>
                            </Button>
                        )}
                    </div>
                    <ResearchFilters
                        lookups={lookups}
                        value={filters}
                        onChange={applyFilters}
                        onReset={resetFilters}
                    />
                </aside>

                <div className="min-w-0">
                    <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                        <div className="flex items-center gap-2">
                            <Sheet open={mobileFiltersOpen} onOpenChange={(open) => {
                                setMobileFiltersOpen(open)
                                if (open) setDraftFilters(filters)
                            }}>
                                <SheetTrigger asChild>
                                    <Button variant="outline" className="lg:hidden">
                                        <Filter className="size-4" />
                                        Bộ lọc
                                        {activeFilterCount > 0 && (
                                            <span className="flex size-5 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
                                                {activeFilterCount}
                                            </span>
                                        )}
                                    </Button>
                                </SheetTrigger>
                                <SheetContent side="left" className="w-[90vw] sm:max-w-md">
                                    <SheetHeader>
                                        <SheetTitle>Bộ lọc kết quả nghiên cứu</SheetTitle>
                                        <SheetDescription>Chọn một hoặc nhiều điều kiện để thu hẹp kết quả.</SheetDescription>
                                    </SheetHeader>
                                    <div className="min-h-0 flex-1 overflow-y-auto px-4 pb-4">
                                        <ResearchFilters
                                            lookups={lookups}
                                            value={draftFilters}
                                            onChange={setDraftFilters}
                                            onReset={() => setDraftFilters(EMPTY_FILTERS)}
                                        />
                                    </div>
                                    <SheetFooter className="border-t border-border">
                                        <Button onClick={() => {
                                            applyFilters(draftFilters)
                                            setMobileFiltersOpen(false)
                                        }}>
                                            Áp dụng bộ lọc
                                        </Button>
                                    </SheetFooter>
                                </SheetContent>
                            </Sheet>
                            <p className="text-sm text-muted-foreground" aria-live="polite">
                                {loading ? "Đang tải..." : `${total} kết quả phù hợp`}
                            </p>
                        </div>

                        <Select value={sort} onValueChange={(value) => updateSort(value as PublicResearchSort)}>
                            <SelectTrigger className="w-44" aria-label="Sắp xếp kết quả">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                {SORT_OPTIONS.map((option) => (
                                    <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    {activeChips.length > 0 && (
                        <div className="mb-5 flex flex-wrap items-center gap-2" aria-label="Bộ lọc đang áp dụng">
                            {activeChips.map((chip) => (
                                <button
                                    key={chip.key}
                                    type="button"
                                    onClick={chip.remove}
                                    className="inline-flex min-h-7 max-w-full items-center gap-1.5 rounded-full bg-secondary px-2.5 py-1 text-xs font-medium text-secondary-foreground hover:bg-secondary/80"
                                    title={`Bỏ lọc ${chip.label}`}
                                >
                                    <span className="truncate">{chip.label}</span>
                                    <X className="size-3.5 shrink-0" aria-hidden="true" />
                                </button>
                            ))}
                            <Button type="button" variant="ghost" size="sm" onClick={resetFilters}>
                                Xóa tất cả
                            </Button>
                        </div>
                    )}

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
                            Không có kết quả phù hợp. Hãy thử bỏ bớt điều kiện lọc.
                        </div>
                    ) : (
                        <div className="grid gap-4">
                            {items.map((research) => (
                                <ResearchCard key={research.research_id} research={research} variant="row" />
                            ))}
                        </div>
                    )}

                    <div className="mt-6 flex flex-col items-center gap-3">
                        <RtlPagination page={page} totalPages={totalPages} onPageChange={updatePage} />
                        <p className="text-xs text-muted-foreground">Trang {page} / {totalPages}</p>
                    </div>
                </div>
            </section>
        </PublicShell>
    )
}

export default function ResearchesPage() {
    return (
        <Suspense fallback={<PublicShell><div className="mx-auto max-w-7xl px-4 py-8">Đang tải...</div></PublicShell>}>
            <ResearchesContent />
        </Suspense>
    )
}
