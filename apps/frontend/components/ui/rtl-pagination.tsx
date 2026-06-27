"use client"

import {
    Pagination,
    PaginationContent,
    PaginationEllipsis,
    PaginationItem,
    PaginationLink,
    PaginationNext,
    PaginationPrevious,
} from "@/components/ui/pagination"
import { cn } from "@/lib/utils"

function getVisiblePages(page: number, totalPages: number) {
    if (totalPages <= 7) {
        return Array.from({ length: totalPages }, (_, index) => index + 1)
    }

    if (page <= 4) {
        return [1, 2, 3, 4, 5, "ellipsis-end", totalPages] as const
    }

    if (page >= totalPages - 3) {
        return [1, "ellipsis-start", totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages] as const
    }

    return [1, "ellipsis-start", page - 1, page, page + 1, "ellipsis-end", totalPages] as const
}

export function RtlPagination({
    page,
    totalPages,
    onPageChange,
    className,
}: {
    page: number
    totalPages: number
    onPageChange: (page: number) => void
    className?: string
}) {
    if (totalPages <= 1) return null

    const goToPage = (nextPage: number) => {
        if (nextPage < 1 || nextPage > totalPages || nextPage === page) return
        onPageChange(nextPage)
    }

    return (
        <Pagination className={cn("justify-end", className)}>
            <PaginationContent>
                <PaginationItem>
                    <PaginationPrevious
                        href="#"
                        text="Trước"
                        aria-disabled={page <= 1}
                        className={cn(page <= 1 && "pointer-events-none opacity-50")}
                        onClick={(event) => {
                            event.preventDefault()
                            goToPage(page - 1)
                        }}
                    />
                </PaginationItem>

                {getVisiblePages(page, totalPages).map((item) => (
                    <PaginationItem key={item}>
                        {typeof item === "number" ? (
                            <PaginationLink
                                href="#"
                                isActive={item === page}
                                onClick={(event) => {
                                    event.preventDefault()
                                    goToPage(item)
                                }}
                            >
                                {item}
                            </PaginationLink>
                        ) : (
                            <PaginationEllipsis />
                        )}
                    </PaginationItem>
                ))}

                <PaginationItem>
                    <PaginationNext
                        href="#"
                        text="Sau"
                        aria-disabled={page >= totalPages}
                        className={cn(page >= totalPages && "pointer-events-none opacity-50")}
                        onClick={(event) => {
                            event.preventDefault()
                            goToPage(page + 1)
                        }}
                    />
                </PaginationItem>
            </PaginationContent>
        </Pagination>
    )
}
