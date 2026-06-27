import Link from "next/link"
import { CalendarDays, FileText, Users } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ResearchCover } from "@/components/public/ResearchCover"
import type { PublicResearchItem } from "@/services/public-search/public-search.service"

const formatDate = (value: string) =>
    new Intl.DateTimeFormat("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric" }).format(new Date(value))

export function ResearchCard({
    research,
    variant = "card",
}: {
    research: PublicResearchItem
    variant?: "card" | "row"
}) {
    const authorNames = research.authors.map((author) => author.full_name).join(", ")

    return (
        <article className={variant === "row" ? "rounded-lg border border-border bg-card p-3 text-card-foreground transition-colors hover:border-foreground/25 sm:p-4" : "rounded-lg border border-border bg-card p-3 text-card-foreground transition-colors hover:border-foreground/25 sm:p-4"}>
            <div className="flex gap-4">
                <ResearchCover src={research.cover_image_url} title={research.title} variant={variant} />
                <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                        <Badge variant="secondary">{research.output_type.name}</Badge>
                        {research.year ? <Badge variant="outline">{research.year}</Badge> : null}
                        <span className="inline-flex items-center gap-1 text-xs text-muted-foreground sm:ml-auto">
                            <CalendarDays className="size-3.5" />
                            {formatDate(research.approved_at)}
                        </span>
                    </div>
                    <h2 className="mt-3 line-clamp-2 text-base font-semibold leading-6 text-foreground">
                        <Link href={`/researches/${research.research_id}`} className="hover:underline">
                            {research.title}
                        </Link>
                    </h2>
                    <p className={variant === "row" ? "mt-2 line-clamp-2 text-sm leading-6 text-muted-foreground sm:line-clamp-3" : "mt-2 line-clamp-3 text-sm leading-6 text-muted-foreground"}>
                        {research.description || "Chưa có mô tả ngắn cho bài nghiên cứu này."}
                    </p>
                    <dl className="mt-4 grid gap-2 text-sm text-muted-foreground">
                        <div className="flex items-center gap-2">
                            <Users className="size-4 shrink-0" />
                            <dt className="sr-only">Tác giả</dt>
                            <dd className="truncate">{authorNames || "Chưa cập nhật tác giả"}</dd>
                        </div>
                        <div className="flex items-center gap-2">
                            <dt className="sr-only">Khoa</dt>
                            <dd className="truncate">{research.department.name}</dd>
                        </div>
                    </dl>
                    <div className="mt-4 flex flex-wrap gap-2">
                        {research.domains.slice(0, variant === "row" ? 3 : 2).map((domain) => (
                            <Badge key={domain.id} variant="outline">
                                {domain.name}
                            </Badge>
                        ))}
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                        {research.keywords.slice(0, variant === "row" ? 5 : 3).map((keyword) => (
                            <Badge key={keyword.id} variant="ghost">
                                {keyword.name}
                            </Badge>
                        ))}
                    </div>
                    <Button asChild variant="outline" size="sm" className="mt-4">
                        <Link href={`/researches/${research.research_id}`}>Xem chi tiết</Link>
                    </Button>
                </div>
            </div>
        </article>
    )
}
