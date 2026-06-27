"use client"

import { useState } from "react"
import { FileText } from "lucide-react"

import { cn } from "@/lib/utils"

export function ResearchCover({
    src,
    title,
    variant = "card",
}: {
    src: string | null
    title: string
    variant?: "card" | "row"
}) {
    const [failed, setFailed] = useState(false)
    const showImage = src && !failed

    return (
        <div
            className={cn(
                "relative shrink-0 overflow-hidden rounded-lg border border-border bg-muted",
                variant === "card" ? "aspect-[3/4] w-24 sm:w-28" : "aspect-[3/4] w-24 sm:w-28"
            )}
        >
            {showImage ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                    src={src}
                    alt={`Ảnh bìa PDF: ${title}`}
                    className="h-full w-full object-cover"
                    loading="lazy"
                    onError={() => setFailed(true)}
                />
            ) : (
                <div className="flex h-full flex-col justify-between bg-background p-3">
                    <div className="flex items-center justify-between">
                        <span className="rounded-sm bg-foreground px-1.5 py-0.5 text-[10px] font-semibold uppercase text-background">
                            PDF
                        </span>
                    </div>
                    <div>
                        <div className="mb-2 h-2 w-2/3 rounded-sm bg-muted-foreground/25" />
                        <div className="mb-2 h-2 w-full rounded-sm bg-muted-foreground/20" />
                        <div className="h-2 w-4/5 rounded-sm bg-muted-foreground/15" />
                    </div>
                    <p className="line-clamp-3 text-xs font-medium leading-4 text-foreground">{title}</p>
                </div>
            )}
        </div>
    )
}
