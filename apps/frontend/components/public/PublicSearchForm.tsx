"use client"

import type React from "react"
import { Search } from "lucide-react"
import { useRouter } from "next/navigation"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function PublicSearchForm({ initialQuery = "" }: { initialQuery?: string }) {
    const router = useRouter()
    const [query, setQuery] = useState(initialQuery)

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        const params = new URLSearchParams()
        const normalized = query.trim()
        if (normalized) {
            params.set("q", normalized)
        }
        router.push(`/researches${params.size ? `?${params.toString()}` : ""}`)
    }

    return (
        <form onSubmit={handleSubmit} className="flex w-full flex-col gap-2 sm:flex-row">
            <label className="sr-only" htmlFor="public-search">
                Tìm kiếm bài nghiên cứu
            </label>
            <Input
                id="public-search"
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Nhập từ khóa cần tìm kiếm..."
                className="h-10 flex-1"
            />
            <Button type="submit" className="h-10 bg-blue-500">
                <Search data-icon="inline-start" />
                Tìm kiếm
            </Button>
        </form>
    )
}
