"use client"

import type React from "react"
import { useEffect, useState } from "react"
import Link from "next/link"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Download, ExternalLink, FileText, Lock, Users } from "lucide-react"
import { toast } from "sonner"

import { PublicShell } from "@/components/public/PublicShell"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import {
    publicSearchService,
    type PublicFile,
    type PublicResearchDetail,
} from "@/services/public-search/public-search.service"
import { useAppSelector } from "@/lib/hooks/hooks"
import { selectIsAuthenticated } from "@/store/slice/auth.slice"

const formatDate = (value: string | null) =>
    value ? new Intl.DateTimeFormat("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric" }).format(new Date(value)) : "Chưa cập nhật"

const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function PublicResearchDetailPage() {
    const params = useParams<{ research_id: string }>()
    const [detail, setDetail] = useState<PublicResearchDetail | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")

    useEffect(() => {
        publicSearchService
            .getPublicResearchDetail(params.research_id)
            .then(setDetail)
            .catch(() => setError("Không tìm thấy bài nghiên cứu public."))
            .finally(() => setLoading(false))
    }, [params.research_id])

    return (
        <PublicShell>
            <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                <Button asChild variant="ghost" size="sm" className="mb-4">
                    <Link href="/researches">
                        <ArrowLeft data-icon="inline-start" />
                        Quay lại danh sách
                    </Link>
                </Button>

                {loading ? (
                    <div className="grid gap-5 lg:grid-cols-[1fr_340px]">
                        <Skeleton className="h-96 rounded-lg" />
                        <Skeleton className="h-72 rounded-lg" />
                    </div>
                ) : error || !detail ? (
                    <div role="status" className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
                        {error}
                    </div>
                ) : (
                    <div className="grid gap-5 lg:grid-cols-[1fr_340px]">
                        <article className="min-w-0">
                            <div className="rounded-lg border border-border bg-card p-5">
                                <div className="flex flex-wrap items-center gap-2">
                                    <Badge variant="secondary">{detail.output_type.name}</Badge>
                                    {detail.year ? <Badge variant="outline">{detail.year}</Badge> : null}
                                    <Badge variant="outline">Phiên bản {detail.version_no}</Badge>
                                </div>
                                <h1 className="mt-4 text-2xl font-semibold leading-9 text-foreground">
                                    {detail.title}
                                </h1>
                                <dl className="mt-5 grid gap-3 text-sm text-muted-foreground sm:grid-cols-2">
                                    <Meta label="Khoa/đơn vị" value={detail.department.name} />
                                    <Meta label="Ngày duyệt công bố" value={formatDate(detail.approved_at)} />
                                    <Meta label="Nhà xuất bản" value={detail.publisher || "Chưa cập nhật"} />
                                    <Meta label="Ngôn ngữ" value={detail.language || "Chưa cập nhật"} />
                                    <Meta label="Ngày phát hành" value={formatDate(detail.date_issued)} />
                                    <Meta label="Mã định danh" value={detail.identifier || "Chưa cập nhật"} />
                                </dl>
                                {detail.external_url ? (
                                    <Button asChild variant="outline" size="sm" className="mt-4">
                                        <a href={detail.external_url} target="_blank" rel="noreferrer">
                                            <ExternalLink data-icon="inline-start" />
                                            Mở liên kết ngoài
                                        </a>
                                    </Button>
                                ) : null}
                            </div>

                            <Section title="Mô tả">
                                <p>{detail.description || "Chưa có mô tả."}</p>
                            </Section>
                            <Section title="Tóm tắt">
                                <p>{detail.abstract || "Chưa có tóm tắt."}</p>
                            </Section>
                            <Section title="Tác giả">
                                <ul className="grid gap-3">
                                    {detail.authors.length === 0 ? (
                                        <li className="text-muted-foreground">Chưa cập nhật tác giả.</li>
                                    ) : (
                                        detail.authors.map((author) => (
                                            <li key={`${author.author_order}-${author.full_name}`} className="rounded-lg border border-border p-3">
                                                <div className="flex items-start gap-2">
                                                    <Users className="mt-0.5 size-4 text-muted-foreground" />
                                                    <div>
                                                        <p className="font-medium text-foreground">{author.full_name}</p>
                                                        <p className="text-sm text-muted-foreground">
                                                            {author.affiliation || "Chưa cập nhật đơn vị"} · {author.author_role}
                                                        </p>
                                                    </div>
                                                </div>
                                            </li>
                                        ))
                                    )}
                                </ul>
                            </Section>
                        </article>

                        <aside className="grid h-fit gap-4">
                            <div className="rounded-lg border border-border bg-card p-4">
                                <h2 className="font-semibold text-foreground">Lĩnh vực</h2>
                                <div className="mt-3 flex flex-wrap gap-2">
                                    {detail.domains.map((domain) => (
                                        <Badge key={domain.id} variant="outline">{domain.name}</Badge>
                                    ))}
                                </div>
                            </div>

                            <div className="rounded-lg border border-border bg-card p-4">
                                <h2 className="font-semibold text-foreground">Từ khóa</h2>
                                <div className="mt-3 flex flex-wrap gap-2">
                                    {detail.keywords.map((keyword) => (
                                        <Badge key={keyword.id} variant="secondary">{keyword.name}</Badge>
                                    ))}
                                </div>
                            </div>

                            <div className="rounded-lg border border-border bg-card p-4">
                                <h2 className="flex items-center gap-2 font-semibold text-foreground">
                                    <FileText className="size-4" />
                                    Tài liệu đính kèm
                                </h2>
                                <div className="mt-3 grid gap-3">
                                    {detail.file_attachments.length === 0 ? (
                                        <p className="text-sm text-muted-foreground">Chưa có file PDF.</p>
                                    ) : (
                                        detail.file_attachments.map((file) => (
                                            <DownloadFile key={file.file_id} researchId={detail.research_id} file={file} />
                                        ))
                                    )}
                                </div>
                            </div>

                            <div className="rounded-lg border border-border bg-card p-4">
                                <h2 className="font-semibold text-foreground">Thông tin khác</h2>
                                <dl className="mt-3 grid gap-2 text-sm text-muted-foreground">
                                    <Meta label="Quyền truy cập" value={detail.access_level} />
                                    <Meta label="Rights" value={detail.rights || " "} />
                                    <Meta label="Nguồn" value={detail.source || " "} />
                                    <Meta label="Liên hệ/quan hệ" value={detail.relation || " "} />
                                </dl>
                            </div>
                        </aside>
                    </div>
                )}
            </div>
        </PublicShell>
    )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
    return (
        <section className="mt-5 rounded-lg border border-border bg-card p-5 text-sm leading-7 text-muted-foreground">
            <h2 className="mb-3 text-base font-semibold text-foreground">{title}</h2>
            {children}
        </section>
    )
}

function Meta({ label, value }: { label: string; value: string }) {
    return (
        <div>
            <dt className="text-xs font-medium uppercase text-muted-foreground">{label}</dt>
            <dd className="mt-1 text-foreground">{value}</dd>
        </div>
    )
}

function DownloadFile({ researchId, file }: { researchId: string; file: PublicFile }) {
    const router = useRouter()
    const isAuthenticated = useAppSelector(selectIsAuthenticated)
    const [loading, setLoading] = useState(false)

    const handleDownload = async () => {
        if (!isAuthenticated) {
            router.push(`/login?next=/researches/${researchId}`)
            return
        }
        setLoading(true)
        try {
            const data = await publicSearchService.createDownloadUrl(researchId, file.file_id)
            window.location.href = data.download_url
        } catch {
            toast.error("Không thể tạo link download file PDF.")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="rounded-lg border border-border p-3">
            <p className="truncate text-sm font-medium text-foreground">{file.original_filename}</p>
            <p className="mt-1 text-xs text-muted-foreground">
                {formatFileSize(file.file_size_bytes)} · {formatDate(file.uploaded_at)}
            </p>
            <Button onClick={handleDownload} disabled={loading} size="sm" className="mt-3 w-full">
                {isAuthenticated ? <Download data-icon="inline-start" /> : <Lock data-icon="inline-start" />}
                {isAuthenticated ? "Tải PDF" : "Đăng nhập để tải"}
            </Button>
        </div>
    )
}
